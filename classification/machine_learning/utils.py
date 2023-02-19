import pandas as pd
import numpy as np




def find_first_page(lst):
            if len(lst) > 0:
                first_page = lst[0]
            else:
                first_page = -1
            return first_page

def is_in_vicinity(a,b,diff):
            if abs(int(a)-int(b)) <= diff:
                return True
            else:
                return False

def find_seq(first_seq,second_seq,third_seq,diff_threshold):
    three_seq = []
    two_first_seq = []
    two_second_third_seq = []
    two_first_third_seq =[]
    f_break_cnt = 0
    while len(first_seq)>0:
        f_break_cnt +=1
        temp_seq = []
        f_page = -1
        s_page = -1
        t_page = -1
        vicinity_found = False
        for i,value in enumerate(second_seq):
            if is_in_vicinity(first_seq[0],value,diff_threshold):
                f_page = first_seq[0]
                if value > s_page:
                    s_page = value
                    vicinity_found=True
            else:
                pass
        for i,value in enumerate(third_seq):
            if is_in_vicinity(first_seq[0],value,diff_threshold*2):
                f_page = first_seq[0]
                if value > t_page:
                    t_page = value
                    vicinity_found=True
            else:
                pass
        if not vicinity_found:
            p = first_seq.pop(0)
        #print(f_page,s_page,t_page)
        if f_page >= 0 and s_page>=0 and t_page>= 0:
            #print("hehefirts")
            temp_seq.extend([i for i in first_seq if i >= f_page and i<=t_page])
            temp_seq.extend([i for i in second_seq if i >= f_page and i<=t_page])
            temp_seq.extend([i for i in third_seq if i >= f_page and i<=t_page])
            if len(temp_seq)>1:
                three_seq.append(temp_seq)     
        if f_page >= 0 and s_page>=0 and t_page<0:
            temp_seq.extend([i for i in first_seq if i >= f_page and i<=s_page])
            temp_seq.extend([i for i in second_seq if i >= f_page and i<=s_page])
            if len(temp_seq)>1:
                two_first_seq.append(temp_seq)    
        if f_page >= 0 and t_page>=0 and s_page<0:
            temp_seq.extend([i for i in first_seq if i >= f_page and i<=t_page])
            temp_seq.extend([i for i in third_seq if i >= f_page and i<=t_page])
            if len(temp_seq)>1:
                two_first_third_seq.append(temp_seq)   
        if f_page<0 and t_page>=0 and s_page >= 0 :
            temp_seq.extend([i for i in second_seq if i >= s_page and i<=t_page])
            temp_seq.extend([i for i in third_seq if i >= s_page and i<=t_page])
            if len(temp_seq)>1:
                two_second_third_seq.append(temp_seq)
        first_seq = list(set(first_seq) - set(temp_seq))
        second_seq = list(set(second_seq) - set(temp_seq))
        third_seq = list(set(third_seq) - set(temp_seq))
        first_seq.sort()
        second_seq.sort()
        third_seq.sort()
        if f_break_cnt >15 :
            break
    if len(second_seq) >0:
        break_cnt = 0
        while len(second_seq)>0:
            break_cnt +=1
            temp_seq = []
            s_page = -1
            t_page = -1
            s_vicinity_found = False
            for i,value in enumerate(third_seq):
                if is_in_vicinity(second_seq[0],value,diff_threshold):
                    s_page = second_seq[0]
                    if value > t_page:
                        t_page = value
                        s_vicinity_found = True
                else:
                    pass
            if not s_vicinity_found:
                p = second_seq.pop(0)
            if s_page>=0 and t_page>= 0:
                temp_seq.extend([i for i in second_seq if i >= s_page and i<=t_page])
                temp_seq.extend([i for i in third_seq if i >= s_page and i<=t_page])
                if len(temp_seq)>1:
                    two_second_third_seq.append(temp_seq)   
            second_seq = list(set(second_seq) - set(temp_seq))
            third_seq = list(set(third_seq) - set(temp_seq))
            second_seq.sort()
            third_seq.sort()
            if break_cnt > 10:
                break
    return three_seq,two_first_seq,two_second_third_seq,two_first_third_seq