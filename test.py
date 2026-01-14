from models.car import Car

car = Car.where(color="rojo").update(color="red")

print(car)
