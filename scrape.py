import subprocess, pickle, os
from main import Scrape

Scrape.register_dates()

register_dates = pickle.load(open('./pkl/register_dates.pkl','rb'))
dir_list = [i for i in os.listdir('./pkl') if i not in ['dict_constituencies.pkl','register_dates.pkl']]

date_list = []
for (date, date_words) in register_dates:
    if date in dir_list:
        pass
    else:
        date_list.append((date, date_words))
        print(date_words)

if __name__ == "__main__":
    for (date, date_words) in date_list:
        subprocess.run('python main.py "'+date+'" "'+date_words+'"')