import json
from datetime import date

gta5_natives = json.load(open('gta5natives.json'))
rdr2_natives = json.load(open('rdr2natives.json'))
gta5_natives_ungrouped = {}


def gta5_return_type_if_compatible(native_data):
    """Returns the GTA 5 return type if there is a native with the same name from the GTA 5 native db"""
    global gta5_natives_ungrouped

    if (native_data['name'] in gta5_natives_ungrouped and
            'results' in gta5_natives_ungrouped[native_data['name']]):
        return gta5_natives_ungrouped[native_data['name']]['results']

    return native_data['return_type']


def gta5_params_if_compatible(native_data):
    """
    Return the parameters from native db for GTA 5 if it has as many of more parameters
    (if there are more, the remaing ones will be from the RDR 2 db)
    """
    global gta5_natives_ungrouped

    if (native_data['name'] in gta5_natives_ungrouped and
            len(native_data['params']) >= len(gta5_natives_ungrouped[native_data['name']]['params']) and
            'params' in gta5_natives_ungrouped[native_data['name']]):
        params = gta5_natives_ungrouped[native_data['name']]['params']
        if len(params) < len(native_data['params']):
            missingParamStartIndex = len(params)
            print(f"Missing params start at {missingParamStartIndex}")
            params += native_data['params'][missingParamStartIndex:]
        return params

    return native_data['params']


def param_texts(return_type, params):
    """
    Generates:
    parameters to be used as parameters of the function
    parameter types to be used as template type parameters
    parameter names to be used as parameters in Native::Invoke
    and returns it as a tuple
    """
    parameter_text = ''
    parameter_type_text = return_type
    parameter_name_text = ''
    for param in params:
        if params.index(param) == 0:
            parameter_name_text += ', '  # The first one is the hash so the comman needs to be added after that
            parameter_type_text += ', '  # The first one is the return type so the comman needs to be added after that
  
        parameter_text += f'{param["type"]} {param["name"]}'
        parameter_type_text += param["type"]
        parameter_name_text += param["name"]
        if params.index(param) < len(params) - 1:
            parameter_text += ", "
            parameter_type_text += ', '
            parameter_name_text += ', '

    return parameter_text, parameter_type_text, parameter_name_text


# Merge all natives for GTA 5 into one dictionary with the name as the key
for native_group_name, native_group in gta5_natives.items():
    named_native_group = {}
    for native_hash, native_data in native_group.items():
        named_native_group[native_data['name']] = native_data
    gta5_natives_ungrouped.update(named_native_group)


# Generate header file
dateStr = date.today().strftime("%d/%m/%Y")
header_file_text = f'// Generated {dateStr} \n\n'

for nativeGroupName, nativeGroup in rdr2_natives.items():
    header_file_text += f'namespace {nativeGroupName} \n{{\n'  # Start of namespace
    for native_hash, native_data in nativeGroup.items():
        return_type = gta5_return_type_if_compatible(native_data)
        params = gta5_params_if_compatible(native_data)

        parameter_text, parameter_type_text, parameter_name_text = param_texts(return_type, params)

        # Native function
        header_file_text += f'    static {return_type} {native_data["name"]}({parameter_text}) {{ return Native::Invoke<{parameter_type_text}>({native_hash}{parameter_name_text}); }} \n'
    header_file_text += '}\n'  # End of namespace


# Write to header file
header_file = open("natives.h", 'w')
header_file.write(header_file_text)
header_file.close()
