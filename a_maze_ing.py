from parsing import parse_config

if __name__ == "__main__":
    config = parse_config()
    for (x,y) in config.items():
        print(x, y)
    print(len(config["ENTRY"]))