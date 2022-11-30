def check_if_detected_xss_attack(data_to_be_validated):
    if "<script>" in data_to_be_validated:
        return True
    return False

def check_if_detected_injection_attack(data_to_be_validated):
    data_to_be_validated=data_to_be_validated.lower()

    if(('select' in data_to_be_validated) and (' ' in data_to_be_validated) and ('true' in data_to_be_validated) ):
        return True

    mid_position = data_to_be_validated.find('=')
    length = len(data_to_be_validated)
    position = mid_position + 1
    right_side = ""
    left_side = ""
    flag = False

    while(position < length):
        if(data_to_be_validated[position].isnumeric()):
            right_side += data_to_be_validated[position]
            position = position + 1
            continue
        else:
            break
    position = mid_position - 1
    while(position >= 0):
        if(data_to_be_validated[position].isnumeric()):
            left_side += data_to_be_validated[position]
            position = position - 1
            continue
        else:
            break
    if(left_side==right_side):
        flag=True
    
    if(('select' in data_to_be_validated) and (' ' in data_to_be_validated) and (flag) ):
        return True

    return False
