![mech meltdown banner](templates/box-strip.png?raw=true)
# Mech Meltdown
A tabeltop board game where two mechs face off for fast paced, card-in-hand gameplay. And, a set of python scrips to simulate and balance said game.

![example cards](example-cards.png?raw=true)
![thermo mech](thermo.jpg?raw=true)
![thermo damedged](thermo-dmg.jpg?raw=true)

## Rules
![rules](templates/meta-rules-23-11-16.png?raw=true)

# Creation Workflow
## Card Creation

Image:
* Create image with dalle3. Some example prompts:
Mech running and gunning
```
A simple, black line drawing of a mech sprinting and firing laser blasts, against a fully white background. The mech's design should convey agility and precision, focusing on the laser shots. The style is clear and minimalistic, with clean lines and no shading or color, creating a bold and impactful visual. Landscape aspect ratio, 3x4.
```

Droid in cockpit, enraged
```
A simple, black line drawing of a droid robot, inspired by the style of 'Elysium', 'Chappie', 'titanfall', or 'I am Mother', depicted as enraged inside a mech cockpit. The robot should look robust and mechanical, with design elements that convey wrath. The minimalistic style with clean lines, without shading or color, creates a clear and impactful image. It is cramped, like the cockpit of a fighter jet. The focus is on the robot's head and shoulders, capturing the essence of rage and recklessness. The background is the mech cockpit. Landscape aspect ratio, 3x4.
```

Human in cockpit, in pain
```
A simple, black line drawing of a cyberpunk mech pilot inside a mech cockpit, depicted as in pain. The pilot should appear cybernetically enhanced and dressed in typical cyberpunk attire, showcasing a blend of human and mechanical elements. The cockpit should be minimalistic yet detailed, suggesting advanced technology and control mechanisms. It is cramped, like the cockpit of a fighter jet. The style should maintain clean lines without shading or color, emphasizing clarity and impact. Focus on the pilot's upper body and head within the cockpit, capturing a moment of wide-eyed panic. The background is plain white. Landscape aspect ratio, 3x4.
```

Component:
```
A simple, black line drawing of a mech's sensor array, a detachable mechanical component. The minimalistic style with clean lines, without shading or color, creates a clear and impactful image. The background is plain white. Landscape aspect ratio, 3x4
```

* [Remove BG](https://new.express.adobe.com/tools/remove-background) if needed
* [Uncrop image](https://clipdrop.co/uncrop) for 3x4 aspect ratio if needed
* If [heavier photo editing is needed](https://www.photopea.com/)
* Crop, remove saturation, etc using ubuntu's shotwell editor (just open img)

## Credits
Credits OpenAI and Dalle3 image generation AI for the images.

## TODO
* Rename 'retire' to 'impound'?
* Try strength of 5x2 magnets?
* Full-size image if no steps?
* Rest of workflow

