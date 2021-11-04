import sys
from nsaph_utils.utils.io_utils import fst2csv


if __name__ == '__main__':
    fst2csv(sys.argv[1])
    print("All Done")


