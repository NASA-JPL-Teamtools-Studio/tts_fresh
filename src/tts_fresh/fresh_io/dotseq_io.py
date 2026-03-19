import json
import pathlib
import sys
from lxml import etree
import pdb
import shlex
import csv
from io import StringIO
from tts_fresh.seqdict import SeqDict, SeqStepType
from pathlib import Path

def build_command_stem_to_argdata_map(cmd_dict_path: pathlib.Path) -> dict:
    command_stem_to_argdata_map = dict()
    for command in etree.parse(cmd_dict_path).findall('Commands/flight_software_command'):
        stem = command.get('mnemonic')
        command_stem_to_argdata_map[stem] = []
        for argument in command.findall('arguments/*'):
            arg_dict = dict()
            if argument.tag == 'numeric_arg':
                arg_dict['emumerated_values'] = []
            elif argument.tag == 'enumerated_arg':
                arg_dict['emumerated_values'] = [{'dict_value':x.get('dict_value'), 'value':x.get('value')} for x in argument.findall('enumerated_value')]
            elif argument.tag == 'string_arg':
                arg_dict['emumerated_values'] = []
            else:
                print(f'Argument value {argument.tag} is not undertood.')
                sys.exit(1)
            arg_dict['tag'] = argument.tag
            arg_dict['dict_name'] = argument.get('dict_name')
            arg_dict['length'] = argument.get('length')
            arg_dict['type'] = argument.get('type')
            arg_dict['units'] = argument.get('units')
            command_stem_to_argdata_map[stem].append(arg_dict)
    
    return command_stem_to_argdata_map

def dotseq_to_seqdict(file_path: pathlib.Path, config: dict) -> SeqDict:

    #Moved this up here when it originally went with the commented out
    #block below because we want to validate the dict path before passing
    #it to dotseq_to_seqjson_style_dict.
    #
    #Also commented out CmdDictReader because my code works right now
    #and I don't want to have to validate that code for NISAR just yet.
    #
    #But for the future, we should investigate which of this code
    #we can rework to work for both NISAR and EURC and any missions
    #that use this in the future.
    if config is not None:
        try:
            #config_dir = pathlib.Path(config['config_dir'])
            project_root = pathlib.Path(__file__).parent.parent #relative to dotseq_io
            cmd_dict_path = project_root.joinpath(config['command_dictionary_path'])
            pdb.set_trace()
            # cmd_dict = CmdDictReader(cmd_dict_path)
        except FileNotFoundError:
            raise FileNotFoundError(f'File not found: {config["command_dictionary_path"]}')


    dict_data = dotseq_to_seqjson_style_dict(file_path, cmd_dict_path)

    if 'id' not in dict_data.keys():
        raise ValueError('Invalid Sequence: id key is required.')

    seq_id = dict_data['id']

    if 'steps' in dict_data.keys():
        seq_steps = dict_data['steps']
        if 'hardware_commands' in dict_data.keys():
            raise ValueError('Invalid Sequence: SEQ JSON files should not have both steps and hardware commands.')
    elif 'hardware_commands' in dict_data.keys():
        seq_steps = dict_data['hardware_commands']
    else:
        raise ValueError('Invalid Sequence: steps key or hardware_commands key is required.')


        #Commented out for NISAR because we do this elsewhere. But might want to bring
        #this back depending on how we decide to unify EURC and NISAR, so not deleting it
        # # check for arg names, if they're not there then add them
        # for s, step in enumerate(seq_steps):
        #     if 'type' not in step.keys():
        #         step['type'] = 'OTHER'
        #     if SeqStepType.from_string(step['type']) == SeqStepType.COMMAND:
        #         for a, arg in enumerate(step['args']):
        #             if 'name' not in arg.keys():
        #                 command = cmd_dict.cmd(step['stem'])
        #                 dict_arg = command.args[a]
        #                 dict_arg_name = dict_arg.name
        #                 arg['name'] = dict_arg_name
        #                 step['args'][a] = arg
        #     seq_steps[s] = step
                    
    return SeqDict.from_step_dicts(id=seq_id, steps=seq_steps)
    

def dotseq_to_seqjson_style_dict(file_path: pathlib.Path, cmd_dict_path: pathlib.Path) -> dict:
    
    dict_data = {'id': '', 'metadata':{}, 'steps':[]}
    try:
        with open(file_path, 'r', encoding='utf-8') as dotseq_file:
            command_stem_to_argdata_map = build_command_stem_to_argdata_map(cmd_dict_path)
            for line in dotseq_file:
                line = line.strip()
                if line[:2] in [';#', '']: 
                    continue
                elif line[0] == ';':
                    linesplit = line.split('=')
                    if len(linesplit) != 2:
                        continue
                    elif linesplit[0][1:] == 'on_board_filename':
                        dict_data['id'] = linesplit[1]
                    else:
                        dict_data['metadata'][linesplit[0][1:]] = linesplit[1]
                elif line[0] in ['A', 'R']:
                    linesplit = line.split(" ", 2)
                    timestamp = linesplit[0]
                    timetag = timestamp[1:]
                    if timestamp[0] == 'A':
                        timetype = 'ABSOLUTE'
                    elif timestamp[0] == 'R':
                        timetype = 'COMMAND_RELATIVE'
                    else:
                        print(f'Time type not understood: {timestamp[0]}')

                    stem = linesplit[1]
                    try:
                        argvals = next(csv.reader(StringIO(linesplit[2])))
                    except:
                        argvals = []
                    step = {
                        'args': [], 
                        'stem': stem, 
                        'time': {
                            'tag': timetag,
                            'type': timetype
                        },
                        'type': 'command'
                        }
                    argmetadata = command_stem_to_argdata_map[stem]
                    if len(argmetadata) != len(argvals):
                        print(f'Mismatch between arguments supplied for {stem} in dotseq file and in dictionary')
                        pdb.set_trace()
                        sys.exit(1)
                    for ii, argval in enumerate(argvals):
                        if argmetadata[ii]['tag'] == 'numeric_arg':
                            if argmetadata[ii]['type'] == 'UNSIGNED_INT':
                                argtype = f'U{argmetadata[ii]['length']}'
                            elif argmetadata[ii]['type'] == 'FLOAT':
                                argtype = f'F{argmetadata[ii]['length']}'
                            elif argmetadata[ii]['type'] == 'INT':
                                argtype = f'I{argmetadata[ii]['length']}'
                            else:
                                print(f'Argument type {argmetadata[ii]['tag']} not understood.')
                                sys.exit(1)
                        elif argmetadata[ii]['tag'] == 'enumerated_arg':
                            try:
                                int(argval)
                                argval = [x for x in argmetadata[ii]['emumerated_values'] if x['value'] == argval][0]['dict_value']
                            except ValueError:
                                pass #if this happens, then it means that the input was a string. Assume that it's the string value
                            argtype = f'ENUM{argmetadata[ii]['length']}' 
                        elif argmetadata[ii]['tag'] == 'string_arg':
                            argtype = 'STRING'
                        else:
                            print(f'Argument value {argmetadata[ii]['tag']} is not undertood.')
                            sys.exit(1)

                        step['args'].append(
                            {
                                'name': argmetadata[ii]['dict_name'],
                                'type': argtype,
                                'value': argval
                            }
                            )                            
                        
                    dict_data['steps'].append(step)
                else:
                    print(f'.seq line not understood: {line}')
                    sys.exit(1)
                    
    except FileNotFoundError:
        print(f'File not found: {file_path}')
        sys.exit(1)
    except json.JSONDecodeError:
        print(f'Invalid JSON format in file: {file_path}')
        sys.exit(1)
    return dict_data


if __name__ == '__main__':
    pdb.set_trace()