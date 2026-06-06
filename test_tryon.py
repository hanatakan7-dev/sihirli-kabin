from ai.try_on_engine import run_virtual_tryon

result = run_virtual_tryon(
    person_image="static/uploads/user.jpg",
    cloth_image="static/clothes/tshirt.png",
    output_image="static/results/result.png"
)

print(result)