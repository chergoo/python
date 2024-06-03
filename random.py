import random

class MatchstickMan:
    def __init__(self, name, health=100, damage=10):
        self.name = name
        self.health = health
        self.damage = damage

    def attack(self, other):
        attack_damage = random.randint(1, self.damage)
        other.health -= attack_damage
        print(f"{self.name}攻击{other.name}，造成{attack_damage}点伤害")

def main():
    player1 = MatchstickMan("Player 1")
    player2 = MatchstickMan("Player 2")

    print("游戏开始！")

    while player1.health > 0 and player2.health > 0:
        print(f"\n{player1.name}: {player1.health}HP  vs  {player2.name}: {player2.health}HP\n")
        player1.attack(player2)
        if player2.health <= 0:
            print(f"{player1.name}获胜！")
            break

        player2.attack(player1)
        if player1.health <= 0:
            print(f"{player2.name}获胜！")
            break

if __name__ == "__main__":
    main()
