import nsepython


def main():
    holidays = nsepython.nse_holidays()
    holidays = holidays['CBM']
    for holiday in holidays:
        with open('nse_holidays.csv', 'a') as f:
            f.write(f"{holiday['tradingDate']}\n")


if __name__ == '__main__':
    main()
