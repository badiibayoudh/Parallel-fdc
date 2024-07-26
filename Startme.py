from datetime import datetime
from multiprocessing import Pool
import time

lst = [(2, 2),  (4, 4), (5, 5),(6,6),(3, 3),]
result = []

def collect_result(val):
    # print(f"writing result {val}")
    return result.append(val)

def mulX(x, y):
    print(f"start process {x} - {y}")
    time.sleep(3)
    print(f"end process {x} - {y}")
    res = x * y
    res_ap = (x, y, res)
    return res_ap

# Apply Async
def test_apply_async():
    result_f = ''
    result_final=[]

    pool = Pool(processes=10)
    for x,y in lst:
         result_f = pool.apply_async(mulX, args=(x,y), callback=collect_result)
         result_final.append(result_f)

    pool.close()
    for f_res in result_final:
        r = f_res.get(timeout=10)
        print(r)

if __name__ == '__main__':
    start = datetime.now()
    test_apply_async()
    print("End Time Apply Async:", (datetime.now() - start).total_seconds())