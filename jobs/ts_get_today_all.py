
import tushare as ts

data = ts.get_today_all()
print(len(data))
if not data is None and len(data) > 0:
    print(data["date"], data["code"])
else:
    print("no data .")
