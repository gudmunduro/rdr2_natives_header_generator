import json
from datetime import date

gta5Natives = json.load(open('gta5natives.json'))
rdr2Natives = json.load(open('rdr2natives.json'))
gta5NativesUngrouped = {}


def gta5_params_if_compatible(nativeData):
    global gta5NativesUngrouped

    if (nativeData['name'] in gta5NativesUngrouped and 
            len(nativeData['params']) >= len(gta5NativesUngrouped[nativeData['name']]['params']) and 
            'params' in gta5NativesUngrouped[nativeData['name']]):
        params = gta5NativesUngrouped[nativeData['name']]['params']
        if len(params) < len(nativeData['params']):
            missingParamStartIndex = len(params)
            print(f"Missing params start at {missingParamStartIndex}")
            params += nativeData['params'][missingParamStartIndex:]
        return params

    return nativeData['params']

def gta5_return_type_if_compatible(nativeData):
    global gta5NativesUngrouped

    if (nativeData['name'] in gta5NativesUngrouped and
            'results' in gta5NativesUngrouped[nativeData['name']]):
        return gta5NativesUngrouped[nativeData['name']]['results']

    return nativeData['return_type']

# Merge all natives for GTA 5 into one dictionary with the name as the key
for nativeGroupName, nativeGroup in gta5Natives.items():
    namedNativeGroup = {}
    for nativeHash, nativeData in nativeGroup.items():
        namedNativeGroup[nativeData['name']] = nativeData
    gta5NativesUngrouped.update(namedNativeGroup)

dateStr = date.today().strftime("%d/%m/%Y")

# Generate header file
headerFileText = f'// Generated {dateStr} \n\n'

for nativeGroupName, nativeGroup in rdr2Natives.items():
    headerFileText += f'namespace {nativeGroupName} \n{{\n'
    for native, nativeData in nativeGroup.items():
        return_type = gta5_return_type_if_compatible(nativeData)
        params = gta5_params_if_compatible(nativeData)

        parameterText = ''
        parameterTypeText = return_type
        parameterNameText = ''
        for param in params:
            if params.index(param) == 0:
                parameterNameText += ', '
                parameterTypeText += ', '
            
            parameterText += f'{param["type"]} {param["name"]}'
            parameterTypeText += param["type"]
            parameterNameText += param["name"]
            if params.index(param) < len(params) - 1:
                parameterText += ", "
                parameterTypeText += ', '
                parameterNameText += ', '

        headerFileText += f'    static {return_type} {nativeData["name"]}({parameterText}) {{ return Native::Invoke<{parameterTypeText}>({native}{parameterNameText}); }} \n'
    headerFileText += '}\n'

# Write to header file
headerFile = open("natives.h", 'w')
headerFile.write(headerFileText)
headerFile.close()
