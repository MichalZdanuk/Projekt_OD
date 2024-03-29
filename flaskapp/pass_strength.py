import math
def calc_entropy(password):
    n = 1
    if(contains_lower(password)):
        n += 26
    if(contains_upper(password)):
        n += 26
    if(contains_number(password)):
        n += 10
    n += contains_special_char(password)

    print("n = " + str(n))
    return len(password)*math.log2(n)

def inform_about_password_strength(entropy):
    if entropy < 50:
        return "Weak password"
    elif entropy >= 50:
        return "Decent password"
    elif entropy > 80:
        return "Strong password"

def contains_number(string):
    return any(char.isdigit() for char in string)

def contains_lower(string):
    for char in string:
        k = char.islower()
        if (k==True):
            return True
    return False
    

def contains_upper(string):
    for char in string:
        k = char.isupper()
        if (k==True):
            return True
    return False
    
def contains_special_char(string):
    k = 0
    special_symbols = "!@#$%^&*()}{\|;:',./<>\"?"
    tab = []
    for char in string:
            if(char in special_symbols):
                    if(char not in tab):
                        k += 1
                        tab.append(char)
            else:
                continue
    return k

def check_if_safe_from_dictionary_attack(password):
    #checking first dictionary - most common passwords
    with open('flaskapp/dictionary_passwords/500-worst-passwords.txt') as myfile:
        if password in myfile.read():
            return False
    #checking first dictionary - most common passwords ex2
    with open('flaskapp/dictionary_passwords/top_common.txt') as myfile:
        if password in myfile.read():
            return False
    #checking most common 50000 polish words with most common suffixes
    if(check_if_in_dict_combination(password)):
        return False
    return True

suffix_list=['','1','123','12345','x','!','?']

def check_if_in_dict_combination(password):
    file1 = open('flaskapp/dictionary_passwords/50000-polish-words.txt', 'r')
    while True:
        line = file1.readline()
        for suf in suffix_list:
            pass_with_suf=line[:-1]+suf
            if(pass_with_suf==password):
                return True
        if not line:
            break
    return False