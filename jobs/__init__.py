
import sys
from os.path import dirname, abspath, join, sep
lib_path = dirname(dirname(abspath(__file__)))
assert lib_path.split(sep)[-1].lower() == 'mf_stock_data_system'
# sys.path.append(lib_path)
sys.path.insert(0, lib_path)
print('lib_path folder appended to path: ', lib_path)
