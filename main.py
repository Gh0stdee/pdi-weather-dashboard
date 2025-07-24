import string

#Check if the user input contains non-alphabetic characters
def AlphabetCheck(city_name:str)->bool:
    for letter in city_name:
        if letter not in string.ascii_letters:
            print("Invalid input.")
            return False
        else:
            print("Valid input.")
            return True

#Get user's input
def get_city_name()->str:
    city_name = input("Input which city's weather you want to check: ")
    valid = AlphabetCheck(city_name)
    
    #TODO add city names into list
    city_list = []
    if valid and city_name in city_list:
        return city_name
    else:
        return get_city_name()

#Get weather info 
def get_weather(city_name:str)->None:
    #TODO Working with APIs
    weather = None
    print(f"{city_name} is {weather} today.")

def main():
    print("Hello from pdi-weather-dashboard!")

if __name__ == "__main__":
    main()
