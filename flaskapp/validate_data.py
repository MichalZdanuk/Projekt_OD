def check_if_detected_xss_attack(data_to_be_validated):
    if "<script>" in data_to_be_validated:
        return True
    return False

def detected_injection_attack():
    pass