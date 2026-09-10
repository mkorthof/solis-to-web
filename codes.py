import helper


''' Solis codes '''


def status():
    return([
        'Standby / Wait',   # 0
        'Waiting',          # 1
        'Checking',         # 2
        'Normal / Generating (MPPT mode)', # 3
        'Fault',            # 4
        'Permanent Fault',  # 5
        'Upgrading',        # 6
    ])


def errors():
    return ({
        1010: { 'message': 'OV-G-V', 'description': 'Over grid voltage' },
        1011: { 'message': 'UN-G-V', 'description': 'Under grid voltage' },
        1012: { 'message': 'OV-G-F', 'description': 'Grid frequency is higher than the set limit' },
        1013: { 'message': 'UN-G-F', 'description': 'Grid frequency is lower than the set limit' },
        1014: { 'message': 'Backfeed_Iac', 'description': 'AC backfeed current is detected' },
        1015: { 'message': 'NO-Grid', 'description': 'The inverter does not detect the utility grid' },
    })


def get_status(code):
    ''' Return State '''
    try:
        return(f'{code}, {status()[int(code)]}')
    except (KeyError, ValueError, TypeError):
        pass
    return(code)


def get_error(code):
    ''' Return warning/fault code with message and description '''
    ''' Try code as str, int and hex '''
    try:
        return(f'Code {code}, {list(errors()[code].values())}')
    except (KeyError, ValueError, TypeError):
        pass
    try:
        return(f'Code {code}, {int(code, 16)} {list(errors()[int(code, 16)].values())}')
    except (KeyError, ValueError, TypeError):
        pass
    try:
        return(f'Code {code}, {list(errors()[int(code)].values())}')
    except (KeyError, ValueError, TypeError):
        pass
    return(code)
