import os
import stat
import string
import uuid
from typing import Any, Dict, Optional, List, Mapping, Sequence

import yaml

from kubragen2.exception import InvalidParamError


class OutputData(str):
    """Base output data class, used to mark some output as special."""
    pass


class OD_Raw(OutputData):
    """Output raw data to file as-is."""
    pass


class OD_FileTemplate(OutputData):
    """Output string replacing files template *"${FILE_fileid}"* with file names."""
    pass


class OutputDataDumper:
    """Base class to data dumper to string."""
    def dump(self, data) -> str:
        if isinstance(data, str):
            return data
        elif isinstance(data, bytes):
            return data.decode('utf-8')
        else:
            return repr(data)


class OutputDataDumperDefault(OutputDataDumper):
    """Default class to data dumper to string, which support file templates."""
    shfiles: Dict

    def __init__(self, shfiles: Dict):
        super().__init__()
        self.shfiles = shfiles

    def dump(self, data) -> str:
        if isinstance(data, OD_FileTemplate):
            return string.Template(data).substitute(self.shfiles)
        return super().dump(data)


class OutputFile:
    """
    Represents a file to be output.

    :param filename: base file name. Suffixes and/or prefixes can be added as needed
    :param is_sequence: whether the file is part of a sequence, if so it will be output with a numbered prefix
    """
    filename: str
    data: List[Any]
    fileid: str
    is_sequence: bool
    reverse: bool

    def __init__(self, filename: str, is_sequence: bool = True, reverse: bool = False):
        self.filename = filename
        self.is_sequence = is_sequence
        self.reverse = reverse
        self.fileid = str(uuid.uuid4()).replace('-', '')
        self.data = []

    def append(self, data: Any) -> None:
        """
        Append data to the file.

        :param data: string or relevant class
        """
        if self.reverse:
            self.data.insert(0, data)
        else:
            self.data.append(data)

    def output_filename(self, seq: Optional[int] = None) -> str:
        """
        Returns the filename that should be output.

        :param seq: the file sequence, if is_sequence is True
        :return: the filename
        """
        if self.is_sequence:
            if seq is None:
                raise InvalidParamError('Sequence is required for sequence files')
            return '{:03d}-{}'.format(seq+1, self.filename)
        else:
            return self.filename

    def file_newline(self) -> Optional[str]:
        """The file newline format, to be passed to the :func:`os.open` function as the "newline" parameter."""
        return None

    def file_encoding(self) -> str:
        """The file encoding, to be passed to the :func:`os.open` function as the "encoding" parameter."""
        return 'utf-8'

    def file_executable(self) -> bool:
        """Whether the file should be marked as executable."""
        return False

    def to_string(self, dumper: OutputDataDumper):
        """
        Output file to string using the dumper.

        :param dumper: dumper to use to output
        """
        ret = []
        for d in self.data:
            if d is None:
                continue
            ret.append(dumper.dump(d))
        return '\n'.join(ret)


class OutputDriver:
    """Driver interface to output files."""


    def write_file(self, file: OutputFile, filename: str, filecontents: Any) -> None:
        """
        Outputs a file.

        :param file: file to output
        :param filename: output file name
        :param filecontents: file contents
        """
        pass


class OutputProject:
    """
    Outputs a list of files, controlling sequence of files that are sequential.
    """
    out_single: List[OutputFile]
    out_sequence: List[OutputFile]

    def __init__(self):
        self.out_single = []
        self.out_sequence = []

    def append(self, outputfile: OutputFile) -> None:
        """
        Appends a file to the project.

        :param outputfile: file to append
        """
        if outputfile.is_sequence:
            self.out_sequence.append(outputfile)
        else:
            self.out_single.append(outputfile)

    def output(self, driver: OutputDriver) -> None:
        """
        Output all files to the driver.

        :param driver: driver to output to
        """
        shfiles = {}
        for fidx, f in enumerate(self.out_sequence):
            shfiles['FILE_{}'.format(f.fileid)] = f.output_filename(fidx)
        for fidx, f in enumerate(self.out_single):
            shfiles['FILE_{}'.format(f.fileid)] = f.output_filename()

        odd = OutputDataDumperDefault(shfiles)

        for fidx, f in enumerate(self.out_sequence):
            driver.write_file(f, f.output_filename(fidx), f.to_string(odd))

        for fidx, f in enumerate(self.out_single):
            driver.write_file(f, f.output_filename(), f.to_string(odd))


#
# IMPL
#

class OutputFile_ShellScript(OutputFile):
    """
    An :class:`kubragen2.output.OutputFile` that is a shell script.
    It is saved with newlines as LF in all platforms, and is marked as executable.
    """
    def __init__(self, filename: str, is_sequence: bool = False, reverse: bool = False):
        super().__init__(filename=filename, is_sequence=is_sequence, reverse=reverse)

    def file_newline(self) -> Optional[str]:
        return '\n'

    def file_executable(self) -> bool:
        return True

    def to_string(self, dumper: OutputDataDumper) -> str:
        ret = [
            '#!/bin/bash',
            '',
            super().to_string(dumper),
            ''
        ]
        return '\n'.join(ret)


class OutputFile_Yaml(OutputFile):
    """
    An :class:`kubragen2.output.OutputFile` that is generic YAML file.
    No special Kubernetes-specific options will be applied.
    """
    def yaml_params(self) -> Mapping[Any, Any]:
        return {'default_flow_style': False, 'sort_keys': False}

    def to_string(self, dumper: OutputDataDumper) -> str:
        if self.data is None:
            return ''
        yaml_dump_params: Mapping[Any, Any] = self.yaml_params()
        ret = []
        is_first: bool = True
        for d in self.data:
            if d is None:
                continue
            if isinstance(d, OD_Raw):
                ret.append(dumper.dump(d))
                continue
            if not is_first:
                ret.append('---')
            if isinstance(d, Sequence) and len(d) == 0:
                continue
            is_first = False
            if not isinstance(d, str) and (isinstance(d, Mapping) or isinstance(d, Sequence)):
                if isinstance(d, Sequence):
                    ret.append(yaml.dump_all(d, Dumper=yaml.SafeDumper, **yaml_dump_params))
                else:
                    ret.append(yaml.dump(d, Dumper=yaml.SafeDumper, **yaml_dump_params))
            else:
                ret.append(dumper.dump(d))
        return '\n'.join(ret)


class OutputFile_Kubernetes(OutputFile_Yaml):
    """
    An :class:`kubragen2.output.OutputFile` that is Kubernetes YAML file.
    Special Kubernetes-specific options can be applied.
    """
    pass


class OutputDriver_Print(OutputDriver):
    """
    An :class:`kubragen2.output.OutputDriver` that prints the files to stdout.
    """
    def write_file(self, file: OutputFile, filename, filecontents) -> None:
        print('****** BEGIN FILE: {} ********'.format(filename))
        print(filecontents)
        print('****** END FILE: {} ********'.format(filename))


class OutputDriver_Directory(OutputDriver):
    """
    An :class:`kubragen2.output.OutputDriver` that writes files to a directory.

    :param path: the output directory
    """
    path: str

    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            os.makedirs(path)

    def write_file(self, file: OutputFile, filename, filecontents) -> None:
        outfilename = os.path.join(self.path, filename)
        with open(outfilename, 'w', newline=file.file_newline(), encoding=file.file_encoding()) as fl:
            fl.write(filecontents)
        if file.file_executable():
            st = os.stat(outfilename)
            os.chmod(outfilename, st.st_mode | stat.S_IEXEC)
