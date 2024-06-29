def hex_to_int(hex_string: str) -> int:
    if hex_string.startswith('#'):
        hex_string = hex_string[1:]
    return int(hex_string, 16)

def rarity_to_string(rarity: int) -> str:
    match rarity:
        case 1:
            return 'common'
        case 2:
            return 'uncommon'
        case 3:
            return 'rare'
        case 4:
            return 'superrare'
        case 5:
            return 'legendary'
        case 6:
            return 'shiny'
        case 7:
            return 'form'
        case 8:
            return 'shinyform'
        case 9:
            return 'gigantamax'
        case 10:
            return 'shinygigantamax'
        case 11:
            return 'golden'
        case _:
            return 'unknown'
        
def rarity_to_formatted_string(rarity: int) -> str:
    match rarity:
        case 1:
            return 'Common'
        case 2:
            return 'Uncommon'
        case 3:
            return 'Rare'
        case 4:
            return 'Super Rare'
        case 5:
            return 'Legendary'
        case 6:
            return 'Shiny'
        case 7:
            return 'Form'
        case 8:
            return 'Shiny Form'
        case 9:
            return 'Gigantamax'
        case 10:
            return 'Shiny Gigantamax'
        case 11:
            return 'Golden'
        case _:
            return 'Unknown'
        
def rarity_to_int(rarity: str) -> int:
    match rarity:
        case 'common':
            return 1
        case 'uncommon':
            return 2
        case 'rare':
            return 3
        case 'superrare':
            return 4
        case 'legendary':
            return 5
        case 'shiny':
            return 6
        case 'form':
            return 7
        case 'shinyform':
            return 8
        case 'gigantamax':
            return 9
        case 'shinygigantamax':
            return 10
        case 'golden':
            return 11
        case _:
            return -1
