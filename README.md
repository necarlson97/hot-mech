# Mech Meltdown
A tabeltop board game where two mechs face off for fast paced, card-in-hand gameplay. And, a set of python scrips to simulate and balance said game.

![example cards](example-cards.png?raw=true)
![thermo mech](thermo.jpg?raw=true)
![thermo damedged](thermo-dmg.jpg?raw=true)

## Credits
Credits OpenAI and Dalle3 image generation AI for the images.

# TODO
* Rethink 'ignore terrain'. Maybe just 'flying'. Do we even care about dealing damaged for 'hitting a wall'?
* Try strength of 5x2 magnets?
* Rules html (and maybe some explainer images)
* Full-size image if no steps?

* Simpily part counts, lower HP:
(can still print separately, but just glue in place - print little 'pucks' for perminient attachement - rather than magnets?)

thermo removable parts now:
per leg = 11 (22)
per arm = 4 (8)
torso = 7

total = 37

If we were to do '10' total:
Feet are 1 part
Torso is just face plate
Hips are joined

So:
Face = 1
Both Thighs = 2
Both Shins = 2
Both bicepts = 2
Both forearms = 2
(pilot?? = 1)

Total = 9 (10??)

Card Creation Workflow:
(todo rest of workflow)

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
* [Remove BG](https://new.express.adobe.com/tools/remove-background) if needed
* [Uncrop image](https://vmake.ai/image-outpainting/upload) for 3x4 aspect ratio if needed
* Crop, remove saturation, etc using ubuntu's shotwell editor (just open img)

