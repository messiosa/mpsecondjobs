import subprocess

date_list = [
    ('220228','28 February 2022'),
    ('220214','14 February 2022'),
    ('220131','31 January 2022'),
    ('220117','17 January 2022'),
    ('220104','4 January 2022'),
    ('211213','13 December 2021'),
    ('211129','29 November 2021'),
    ('211115','15 November 2021'),
    ('211101','1 November 2021'),
    ('211018','18 October 2021'),
    ('211004','4 October 2021'),
    ('210920','20 September 2021'),
    ('210906','6 September 2021'),
    ('210823','23 August 2021'),
    ('210726','26 July 2021'),
    ('210712','12 July 2021'),
    ('210628','28 June 2021'),
    ('210614','14 June 2021'),
    ('210601','1 June 2021'),
    ('210517','17 May 2021')
]

if __name__ == "__main__":
    for (date, date_words) in date_list:
        subprocess.run('python3 main.py "'+date+'" "'+date_words+'"')