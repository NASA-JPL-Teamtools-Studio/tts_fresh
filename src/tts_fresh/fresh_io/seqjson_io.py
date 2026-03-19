from tts_seq.core.seqjson_dict import *
from tts_utilities.logger import create_logger
logger = create_logger(__file__)
logger.warning('''
	fresh.fresh_io.seqjson_io has been moved to tts_seq.
	In order to silence this warning and future-proof your
	code, change all imports of fresh.fresh_io.seqjson_io
	to tts_seq.core.seqjson_dict. There is currently no
	immediate plan to remove fresh.fresh_io.seqjson_io, 
	but better to replace it now and not worry about the 
	future
	''')