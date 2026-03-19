from tts_seq.core.seqdict import *
from tts_utilities.logger import create_logger
logger = create_logger(__file__)
logger.warning('''
	tts_fresh.fresh_io.seqjson_io has been moved to tts_seq.
	In order to silence this warning and future-proof your
	code, change all imports of tts_fresh.fresh_io.seqjson_io
	to tts_seq.core.seqjson_dict. There is currently no
	immediate plan to remove tts_fresh.fresh_io.seqjson_io, 
	but better to replace it now and not worry about the 
	future
	''')