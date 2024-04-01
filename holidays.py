import nsepython


def main():
    holidays = nsepython.nse_holidays(type="trading")
    holidays = holidays['FO']
    holiday_dates = [holiday['tradingDate'] for holiday in holidays]

    with open('nse_holidays.csv', 'w') as f:
        f.write("\n".join(holiday_dates))


if __name__ == '__main__':
    main()
