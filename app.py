from flask import Flask, request
import telebot
import json

app = Flask(__name__)
bot_token = "7284578589:AAGX6Hz4aaN2OOATB3mfBw7WwElWfmStvxQ"
bot = telebot.TeleBot(bot_token)

OPTIONS = ["Comprar", "Catalogo", "Contacto", "Carrito"]
guitarras = ["Gibson", "Fender", "Godin", "Martin", "Gretsch", "Epiphone", "Ibanez"]
carts = {}
total_amounts = {}
guitarras_list_dict = []
user_start = {}

def save_data_to_file():
    with open ('guitarras_data.json', 'w') as file:
        json.dump(guitarras_list_dict, file, indent=4)

def load_data_from_file():
    global guitarras_list_dict
    try: 
        with open('guitarras_data.json', 'r') as file:
            guitarras_list_dict = json.load(file)
    except FileNotFoundError:
        guitarras_list_dict = []

def save_cart_data():
    with open('cart_data.json', 'w') as file:
        json.dump(carts, file, indent=4)
    print("Cart data saved:", carts)
    with open('total_amounts.json', 'w') as file:
        json.dump(total_amounts, file, indent=4)

def load_cart_data():
    global carts, total_amounts
    try:
        with open('cart_data.json', 'r') as file:
            carts = json.load(file)
        with open('total_amounts.json', 'r') as file:
            total_amounts = json.load(file)
        print("Cart data loaded successfully.", carts, total_amounts)
    except FileNotFoundError:
        print("Cart data file not found, creating new files.")
        carts = {}
        total_amounts = {}
        save_cart_data()  # Create the files if they don't exist
    except json.JSONDecodeError:
        carts = {}
        total_amounts = {}
        print("Error decoding cart data. Initialized empty cart.")

load_data_from_file()
load_cart_data()

def init_dict():
    global guitarras_list_dict
    if not guitarras_list_dict:
        for i, m in enumerate(guitarras):
            i = i + 1
            guitarras_dict = {"id": i, "marca": m}
            if m == "Gibson":
                guitarras_dict["price"] = 2500
                guitarras_dict["model"] = "Les Paul"
                guitarras_dict["type"] = "Electric"
                guitarras_dict["Stock"] = 5

            elif m == "Fender":
                guitarras_dict["price"] = 1500
                guitarras_dict["model"] = "Stratocaster"
                guitarras_dict["type"] = "Electric"
                guitarras_dict["Stock"] = 9

            elif m == "Gretsch":
                guitarras_dict["price"] = 1200
                guitarras_dict["model"] = "Electromatic"
                guitarras_dict["type"] = "Semihollow"
                guitarras_dict["Stock"] = 7
                
            elif m == "Godin":
                guitarras_dict["price"] = 2000
                guitarras_dict["model"] = "A6 ULTRA"
                guitarras_dict["type"] = "Electro classic"
                guitarras_dict["Stock"] = 3

            elif m == "Ibanez":
                guitarras_dict["price"] = 500
                guitarras_dict["model"] = "Gio"
                guitarras_dict["type"] = "Electric"
                guitarras_dict["Stock"] = 15

            elif m == "Epiphone":
                guitarras_dict["price"] = 600
                guitarras_dict["model"] = "SG"
                guitarras_dict["type"] = "Electric"
                guitarras_dict["Stock"] = 14

            elif m == "Martin":
                guitarras_dict["price"] = 1600
                guitarras_dict["model"] = "Grand J-16E"
                guitarras_dict["type"] = "Electro Acoustic"
                guitarras_dict["Stock"] = 6
                
            guitarras_list_dict.append(guitarras_dict)

init_dict()

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Bienvenido a Dopamina Guitars! Use /menu to start.")

@bot.message_handler(commands=['menu'])
def menu(message):
    menu_text = "Seleccione la opción deseada:\n"
    for i, option in enumerate(OPTIONS, 1):
        menu_text += f"{i}. {option}\n"
    bot.reply_to(message, menu_text)

@bot.message_handler(commands=['catalogo'])
def send_catalog(message):
    text = "\n📚 *Catálogo de Guitarras🎸:*\n"
    for guitar in guitarras_list_dict:
        text += (
            f"\n*{guitar['id']}. {guitar['marca']} {guitar['model']}*\n"
            f"Tipo: {guitar['type']}\n"
            f"Precio: ${guitar['price']} USD\n"
            f"Stock: {guitar['Stock']}\n"
            "---------------------------"
        )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['comprar'])
def comprar(message):

    bot.reply_to(message, "Seleccione las guitarras que le interesa comprar:")
    bot.register_next_step_handler(message, add_to_cart)

def add_to_cart(message):
    guitar_id = message.text.strip()
    user_id = str(message.from_user.id)

    try:
        guitar_id = int(guitar_id)
        selected_guitar = next((g for g in guitarras_list_dict if g['id'] == guitar_id), None)
        if selected_guitar:
            if selected_guitar['Stock'] > 0:
                if user_id not in carts:
                    carts[user_id] = []
                    total_amounts[user_id] = 0
                carts[user_id].append(selected_guitar)
                total_amounts[user_id] += selected_guitar['price']
                selected_guitar['Stock'] -= 1

                save_data_to_file()
                save_cart_data()

                bot.reply_to(message, f"{selected_guitar['marca']} {selected_guitar['model']} Añadida a su carrito. Total: ${total_amounts[user_id]} USD")
            else:
                bot.reply_to(message, "Lo siento, esta guitarra está agotada.")

        else: 
            bot.reply_to(message, "Guitarra no encontrada, intente nuevamente.")
    except ValueError:
        bot.reply_to(message, "Entrada no válida. Por favor intente de nuevo.")

            
@bot.message_handler(commands=['carrito'])
def carrito(message):
    user_id = str(message.from_user.id)
    print("User ID:", user_id)
    print("Current carts:", carts)
    print("Current total_amounts:", total_amounts)

    if user_id in carts and carts[user_id]:
        cart_text = "🛒 *Su Carrito de Compras:*\n"
        for guitar in carts[user_id]:
            cart_text += f"- {guitar['marca']} {guitar['model']}: ${guitar['price']} USD\n"
        cart_text += f"\nTotal: ${total_amounts[user_id]} USD"
        bot.send_message(message.chat.id, cart_text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Su carrito está vacío.")

@bot.message_handler(commands=['eliminar'])
def eliminar(message):
    user_id = str(message.from_user.id)
    if user_id in carts and carts[user_id]:
        cart_text = "🛒 *Seleccione el número de la guitarra que desea eliminar:*\n"
        for i, guitar in enumerate(carts[user_id], 1):
            cart_text += f"{i}. {guitar['marca']} {guitar['model']}: ${guitar['price']} USD\n"
        bot.send_message(message.chat.id, cart_text, parse_mode='Markdown')
        bot.register_next_step_handler(message, process_delete_item)
    else:
        bot.reply_to(message, "Su carrito está vacío.")

def process_delete_item(message):
    try:
        item_number = int(message.text.strip()) - 1
        user_id = str(message.from_user.id)

        if user_id in carts and 0 <= item_number < len(carts[user_id]):
            deleted_guitar = carts[user_id].pop(item_number)
            total_amounts[user_id] -= deleted_guitar['price']
            save_cart_data()
            for guitar in guitarras_list_dict:
                if guitar['id'] == deleted_guitar['id']:
                    guitar['Stock'] += 1
                    break
            save_data_to_file()
            bot.reply_to(message, f"{deleted_guitar['marca']} {deleted_guitar['model']} fue eliminada de su carrito. Total: ${total_amounts[user_id]} USD")
        else:
            bot.reply_to(message, "Número de artículo inválido. Intente de nuevo.")
    except ValueError:
        bot.reply_to(message, "Entrada no válida. Por favor, introduzca un número válido.")

@bot.message_handler(commands=['add_guitar'])
def add_guitar(message):
    bot.reply_to(
        message,
        "Por favor, proporcione los detalles de la guitarra en el siguiente formato:\n\n"
        "*Marca*, *Modelo*, *Precio*, *Tipo*, *Stock*\n\n"
        "Ejemplo:\nGibson, SG, 2000, Electric, 15",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, process_guitar_details)

def process_guitar_details(message):
    print("Processing guitar details...")
    details = [detail.strip() for detail in message.text.split(',', 4)]
    print("Details received:", details)
    
    if len(details) != 5:
        print("Invalid number of details.")
        bot.reply_to(message, "Please provide all details in the format: brand, model, price, type, stock.\nFor example: Gibson, SG, 2000, Electric, 15")
        return
    
    brand, model, price, type, stock = details
    
    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        print("Error in price or stock conversion.")
        bot.reply_to(message, "Price must be a number and stock must be an integer.")
        return

    global guitarras_list_dict
    new_guitar = {
        "id": len(guitarras_list_dict) + 1,
        "marca": brand,
        "model": model,
        "price": price,
        "type": type,
        "Stock": stock
    }
    guitarras_list_dict.append(new_guitar)
    print(f"Guitar added: {brand} {model}, ${price}, {type}, {stock} in stock.")
    save_data_to_file()
    bot.reply_to(message, f"Guitar added: {brand} {model}, ${price}, {type}, {stock} in stock.")

@app.route('/' + bot_token, methods=['POST'])
def getMessage():
    print("Received POST request")
    json_str = request.get_data().decode('UTF-8')
    print("Received update:", json_str)
    update = telebot.types.Update.de_json(json_str)
    print("Parsed update:", update)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://31a2-2001-1308-1c30-7300-5c54-fc31-1c1b-3b32.ngrok-free.app/' + bot_token)
    return "Webhook set", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)