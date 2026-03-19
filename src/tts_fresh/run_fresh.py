 import argparse, pathlib

from tts_fresh.check_frs import check_frs_from_file
from tts_fresh.mission_config import get_io_method, get_default_config_file

def main() -> None:
    """
    Acts as the main entry point for the FRESH command-line interface. 
    It defines and parses command-line arguments to control sequence input, report output, 
    and tool behavior, eventually delegating the execution to the core validation logic.

    :return: None
    :rtype: None
    """
    # set up args
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i',
        '--input-file',
        type=pathlib.Path,
        help='The sequence file to check',
        required=True
    )
    ap.add_argument(
        '-o',
        '--output-file',
        type=pathlib.Path, 
        help="Custom output file path.",
        required=False
    )
    ap.add_argument(
        '-c',
        '--config-file',
        type=pathlib.Path, 
        help="Path to config file",
        required=False,
        default=pathlib.Path.joinpath(pathlib.Path(__file__).absolute().parent, "config", get_default_config_file())
    )
    ap.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="Whether to print information to the console while running.",
        required=False
    )
    ap.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help="Whether to suppress individual PASSED results in the FRESH report.",
        required=False
    )
    args = ap.parse_args()

    check_frs_from_file(
        io_method=get_io_method(),
        input_file=args.input_file, 
        output_file=args.output_file,
        config_file=args.config_file,
        verbose=args.verbose,
        quiet=args.quiet
    )


if __name__ == '__main__':
    main()