# Add parent dir to path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from bodylogger import check_date

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


if __name__ == '__main__':
    test_check_date()
