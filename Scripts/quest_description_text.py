"""Concise player-facing wording for repeatable quest acceptance dialogue."""

PURPOSES = {
    'Clinic Restock': 'the clinic',
    'Research Commission': 'his research',
    'Sealed Guild Order': 'a guild order',
    'Emergency Reserve': 'our emergency supplies',
}
ENEMY_PLURALS = {
    'Forest Slime': 'forest slimes', 'Wild Boar': 'wild boars',
    'Cave Bat': 'cave bats', 'Thorn Wolf': 'thorn wolves',
    'Road Bandit': 'road bandits', 'Moss Beetle': 'moss beetles',
    'Stone Wisp': 'stone wisps', 'Marsh Spider': 'marsh spiders',
    'Ash Imp': 'ash imps', 'Rogue Golem': 'rogue golems',
}

def format_quest_description(quest):
    kind = quest['objectiveType']
    if kind == 'Combat':
        enemy = quest['title'].split(': ', 1)[1].split(' Hunt - ', 1)[0]
        plural = ENEMY_PLURALS[enemy]
        speech = f"We've had reports of {plural} nearby. Defeat {quest['requiredAmount']}, then report back to me."
    else:
        material, context = quest['deliveryTitle'].split(': ', 1)[1].split(' - ', 1)
        material = material.lower()
        purpose = PURPOSES[context]
        if kind == 'Collection':
            purpose = 'guild research' if context == 'Research Commission' else purpose
            speech = f"We need {quest['requiredAmount']} samples of {material} for {purpose}. Gather them, then bring them back to me."
        elif kind == 'Delivery':
            speech = f"Could you deliver these {material} to Rein? He needs them for {purpose}."
        else:
            raise ValueError(f'Unknown objective type: {kind}')
    stars = '\u2605' * quest['stars'] + '\u2606' * (5 - quest['stars'])
    return f"{speech}\n\n{stars}  |  {quest['gold']:,} gold"
