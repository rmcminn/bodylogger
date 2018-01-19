# Add parent dir to path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from bodylogger import check_date
from bodylogger import str_to_sec
from bodylogger import sec_to_str

def test_check_date():
    assert check_date('11/11/2017') == False
    assert check_date('11/11/17') == False
    assert check_date('1/15/2017') == False
    assert check_date('1/1/2017') == False
    assert check_date('1/1/2017') == False
    assert check_date('2017-15-1') == False
    assert check_date('2017-1-1') == '2017-1-1'
    assert check_date('2017-11-12') == '2017-11-12'
    assert check_date('2017-01-01') == '2017-1-1'
    assert check_date('2017-1-01') == '2017-1-1'

def test_str_to_sec():
    assert str_to_sec('00:30:23') == 1823
    assert str_to_sec('00:45:17') == 2717
    assert str_to_sec('00:05:45') == 345
    assert str_to_sec('01:34:16') == 5656
    assert str_to_sec('10:34:16') == 38056    

def test_sec_to_str():
    assert sec_to_str(1823) == '00:30:23'
    assert sec_to_str(2717) == '00:45:17'
    assert sec_to_str(345) == '00:05:45'
    assert sec_to_str(5656) == '01:34:16'
    assert sec_to_str(38056) == '10:34:16'  

if __name__ == '__main__':
    test_check_date()
    test_str_to_sec()
    test_sec_to_str()
