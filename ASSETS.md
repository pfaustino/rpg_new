# Asset Specifications

This document outlines the specifications and requirements for game assets including images, icons, sounds, and animations.

## Directory Structure

```
assets/
├── images/
│   ├── characters/
│   ├── items/
│   ├── ui/
│   └── tiles/
├── sounds/
│   ├── effects/
│   ├── music/
│   └── voice/
└── animations/
    ├── characters/
    ├── effects/
    └── ui/
```

## Image Assets

### Character Sprites
- **Directory**: `assets/images/characters/`
- **Format**: PNG with transparency
- **Dimensions**: 32x32 pixels (TILE_SIZE)
- **Naming Convention**: `character_[name]_[state].png`
  - Example: `character_player_idle.png`, `character_player_walk.png`
- **Animation Requirements**:
  - Idle: 4 frames (facing N, E, S, W)
  - Walk: 4 frames per direction (16 total)
  - Attack: 4 frames per direction (16 total)
  - Death: 4 frames

### Item Icons
- **Directory**: `assets/images/items/`
- **Format**: PNG with transparency
- **Dimensions**: 32x32 pixels
- **Naming Convention**: `item_[type]_[name].png`
  - Example: `item_weapon_sword.png`, `item_armor_helmet.png`
- **Categories**:
  - Weapons
  - Armor
  - Consumables
  - Quest Items

#### Required Weapon Images
- **Base Types**:
  - `item_weapon_sword.png` - Basic sword shape
  - `item_weapon_axe.png` - Basic axe shape
  - `item_weapon_mace.png` - Basic mace shape
  - `item_weapon_bow.png` - Basic bow shape
  - `item_weapon_staff.png` - Basic staff shape
  - `item_weapon_dagger.png` - Basic dagger shape

- **Material Overlays**:
  - `item_material_iron.png` - Iron material texture
  - `item_material_steel.png` - Steel material texture
  - `item_material_silver.png` - Silver material texture
  - `item_material_gold.png` - Gold material texture
  - `item_material_obsidian.png` - Obsidian material texture
  - `item_material_crystal.png` - Crystal material texture

- **Quality Effects**:
  - `item_quality_common.png` - Common quality glow
  - `item_quality_uncommon.png` - Uncommon quality glow
  - `item_quality_rare.png` - Rare quality glow
  - `item_quality_epic.png` - Epic quality glow
  - `item_quality_legendary.png` - Legendary quality glow

#### Required Armor Images
- **Base Types**:
  - `item_armor_helmet.png` - Basic helmet shape
  - `item_armor_chest.png` - Basic chest armor shape
  - `item_armor_legs.png` - Basic leg armor shape
  - `item_armor_boots.png` - Basic boots shape
  - `item_armor_gloves.png` - Basic gloves shape
  - `item_armor_shield.png` - Basic shield shape

- **Material Overlays**:
  - `item_material_leather.png` - Leather material texture
  - `item_material_chain.png` - Chain mail texture
  - `item_material_plate.png` - Plate armor texture
  - `item_material_scale.png` - Scale armor texture
  - `item_material_dragon.png` - Dragon scale texture
  - `item_material_magic.png` - Magic armor texture

- **Quality Effects**:
  - `item_quality_common.png` - Common quality glow
  - `item_quality_uncommon.png` - Uncommon quality glow
  - `item_quality_rare.png` - Rare quality glow
  - `item_quality_epic.png` - Epic quality glow
  - `item_quality_legendary.png` - Legendary quality glow

#### Procedural Generation Notes
1. **Weapon Generation**:
   - Base weapon image is selected based on weapon type
   - Material overlay is applied based on material type
   - Quality effect is overlaid based on item quality
   - All overlays should maintain transparency for proper layering

2. **Armor Generation**:
   - Base armor image is selected based on armor type and slot
   - Material overlay is applied based on material type
   - Quality effect is overlaid based on item quality
   - All overlays should maintain transparency for proper layering

3. **Color Tinting**:
   - Base images should be in grayscale
   - Color is applied procedurally based on material and quality
   - Quality effects should use semi-transparent overlays

4. **Special Effects**:
   - Legendary items may require additional effect overlays
   - Magic items may require particle effect textures
   - Unique items may require custom overlays

### UI Elements
- **Directory**: `assets/images/ui/`
- **Format**: PNG with transparency
- **Dimensions**:
  - Buttons: 128x32 pixels
  - Icons: 24x24 pixels
  - Backgrounds: 800x600 pixels (SCREEN_WIDTH x SCREEN_HEIGHT)
- **Naming Convention**: `ui_[element]_[state].png`
  - Example: `ui_button_normal.png`, `ui_button_hover.png`

### Tile Sets
- **Directory**: `assets/images/tiles/`
- **Format**: PNG with transparency
- **Dimensions**: 32x32 pixels
- **Naming Convention**: `tile_[type]_[variant].png`
  - Example: `tile_floor_stone.png`, `tile_wall_brick.png`
- **Categories**:
  - Floor
  - Wall
  - Decoration
  - Special

#### Floor Tiles
- **Base Types**:
  - `tile_floor_stone.png` - Basic stone floor
  - `tile_floor_wood.png` - Wooden floor
  - `tile_floor_dirt.png` - Dirt floor
  - `tile_floor_grass.png` - Grass floor
  - `tile_floor_sand.png` - Sand floor
  - `tile_floor_water.png` - Water surface
  - `tile_floor_lava.png` - Lava surface
  - `tile_floor_ice.png` - Ice floor

- **Variants**:
  - `tile_floor_stone_cracked.png` - Cracked stone
  - `tile_floor_stone_mossy.png` - Mossy stone
  - `tile_floor_wood_plank.png` - Wooden planks
  - `tile_floor_wood_rotten.png` - Rotten wood
  - `tile_floor_grass_flowers.png` - Flowered grass
  - `tile_floor_grass_tall.png` - Tall grass
  - `tile_floor_sand_dunes.png` - Sand dunes
  - `tile_floor_water_shallow.png` - Shallow water
  - `tile_floor_water_deep.png` - Deep water

#### Wall Tiles
- **Base Types**:
  - `tile_wall_stone.png` - Stone wall
  - `tile_wall_brick.png` - Brick wall
  - `tile_wall_wood.png` - Wooden wall
  - `tile_wall_dirt.png` - Dirt wall
  - `tile_wall_metal.png` - Metal wall
  - `tile_wall_crystal.png` - Crystal wall
  - `tile_wall_ice.png` - Ice wall
  - `tile_wall_lava.png` - Lava wall

- **Variants**:
  - `tile_wall_stone_cracked.png` - Cracked stone
  - `tile_wall_stone_mossy.png` - Mossy stone
  - `tile_wall_brick_old.png` - Old brick
  - `tile_wall_brick_broken.png` - Broken brick
  - `tile_wall_wood_plank.png` - Wooden planks
  - `tile_wall_wood_rotten.png` - Rotten wood
  - `tile_wall_metal_rusty.png` - Rusty metal
  - `tile_wall_metal_shiny.png` - Shiny metal
  - `tile_wall_crystal_blue.png` - Blue crystal
  - `tile_wall_crystal_red.png` - Red crystal

#### Decoration Tiles
- **Furniture**:
  - `tile_deco_table.png` - Basic table
  - `tile_deco_chair.png` - Basic chair
  - `tile_deco_chest.png` - Basic chest
  - `tile_deco_bed.png` - Basic bed
  - `tile_deco_bookshelf.png` - Bookshelf
  - `tile_deco_barrel.png` - Barrel
  - `tile_deco_crate.png` - Crate
  - `tile_deco_pillar.png` - Pillar

- **Nature**:
  - `tile_deco_tree.png` - Tree
  - `tile_deco_bush.png` - Bush
  - `tile_deco_rock.png` - Rock
  - `tile_deco_flower.png` - Flower
  - `tile_deco_grass.png` - Grass tuft
  - `tile_deco_mushroom.png` - Mushroom
  - `tile_deco_vine.png` - Vine
  - `tile_deco_web.png` - Spider web

- **Lighting**:
  - `tile_deco_torch.png` - Wall torch
  - `tile_deco_lantern.png` - Hanging lantern
  - `tile_deco_candle.png` - Candle
  - `tile_deco_crystal.png` - Glowing crystal

#### Special Tiles
- **Doors**:
  - `tile_special_door_wood.png` - Wooden door
  - `tile_special_door_metal.png` - Metal door
  - `tile_special_door_crystal.png` - Crystal door
  - `tile_special_door_secret.png` - Secret door

- **Stairs**:
  - `tile_special_stairs_up.png` - Stairs up
  - `tile_special_stairs_down.png` - Stairs down
  - `tile_special_stairs_spiral.png` - Spiral stairs

- **Traps**:
  - `tile_special_trap_spikes.png` - Spike trap
  - `tile_special_trap_arrow.png` - Arrow trap
  - `tile_special_trap_pit.png` - Pit trap
  - `tile_special_trap_poison.png` - Poison trap

- **Interactive**:
  - `tile_special_lever.png` - Lever
  - `tile_special_button.png` - Button
  - `tile_special_pressure.png` - Pressure plate
  - `tile_special_altar.png` - Altar

#### Tile Set Notes
1. **Variants**:
   - Each base tile should have at least 2-3 variants
   - Variants should maintain consistent style and dimensions
   - Variants should be easily distinguishable from base tiles

2. **Transitions**:
   - Create transition tiles between different floor types
   - Create corner and edge tiles for walls
   - Create blending tiles for natural elements

3. **Layering**:
   - Decoration tiles should work on top of floor tiles
   - Some decorations may require multiple layers
   - Consider shadow and lighting effects

4. **Animation**:
   - Water and lava tiles may require animation frames
   - Torches and other light sources may need flickering
   - Traps may need activation/deactivation states

## Sound Assets

### Sound Effects
- **Directory**: `assets/sounds/effects/`
- **Format**: WAV or OGG
- **Sample Rate**: 44.1kHz
- **Bit Depth**: 16-bit
- **Channels**: Mono or Stereo
- **Naming Convention**: `sfx_[action]_[variant].wav`
  - Example: `sfx_swing_1.wav`, `sfx_hit_2.wav`

#### Combat Effects
- **Weapon Sounds**:
  - `sfx_sword_swing_1.wav` - Sword swing
  - `sfx_sword_hit_1.wav` - Sword impact
  - `sfx_axe_swing_1.wav` - Axe swing
  - `sfx_axe_hit_1.wav` - Axe impact
  - `sfx_bow_draw_1.wav` - Bow draw
  - `sfx_arrow_release_1.wav` - Arrow release
  - `sfx_arrow_hit_1.wav` - Arrow impact
  - `sfx_magic_cast_1.wav` - Spell casting
  - `sfx_magic_hit_1.wav` - Spell impact

- **Armor Sounds**:
  - `sfx_armor_metal_1.wav` - Metal armor movement
  - `sfx_armor_leather_1.wav` - Leather armor movement
  - `sfx_shield_block_1.wav` - Shield block
  - `sfx_shield_break_1.wav` - Shield break

- **Combat States**:
  - `sfx_critical_hit_1.wav` - Critical hit
  - `sfx_miss_1.wav` - Attack miss
  - `sfx_dodge_1.wav` - Successful dodge
  - `sfx_parry_1.wav` - Successful parry
  - `sfx_death_1.wav` - Character death

#### Movement Effects
- **Footsteps**:
  - `sfx_footstep_stone_1.wav` - Stone floor
  - `sfx_footstep_wood_1.wav` - Wooden floor
  - `sfx_footstep_grass_1.wav` - Grass
  - `sfx_footstep_water_1.wav` - Water
  - `sfx_footstep_sand_1.wav` - Sand

- **Actions**:
  - `sfx_jump_1.wav` - Jump
  - `sfx_land_1.wav` - Landing
  - `sfx_roll_1.wav` - Roll/dodge
  - `sfx_climb_1.wav` - Climbing
  - `sfx_swim_1.wav` - Swimming

#### UI Effects
- **Buttons**:
  - `sfx_button_hover_1.wav` - Button hover
  - `sfx_button_click_1.wav` - Button click
  - `sfx_button_confirm_1.wav` - Confirm action
  - `sfx_button_cancel_1.wav` - Cancel action

- **Notifications**:
  - `sfx_notification_1.wav` - General notification
  - `sfx_quest_complete_1.wav` - Quest completion
  - `sfx_level_up_1.wav` - Level up
  - `sfx_item_pickup_1.wav` - Item pickup
  - `sfx_inventory_open_1.wav` - Inventory open
  - `sfx_inventory_close_1.wav` - Inventory close

#### Environment Effects
- **Weather**:
  - `sfx_rain_1.wav` - Rain
  - `sfx_thunder_1.wav` - Thunder
  - `sfx_wind_1.wav` - Wind
  - `sfx_snow_1.wav` - Snow

- **Ambient**:
  - `sfx_cave_1.wav` - Cave ambience
  - `sfx_forest_1.wav` - Forest ambience
  - `sfx_town_1.wav` - Town ambience
  - `sfx_dungeon_1.wav` - Dungeon ambience
  - `sfx_river_1.wav` - River flow
  - `sfx_fire_1.wav` - Fire crackling

### Music
- **Directory**: `assets/sounds/music/`
- **Format**: OGG
- **Sample Rate**: 44.1kHz
- **Bit Depth**: 16-bit
- **Channels**: Stereo
- **Naming Convention**: `music_[area]_[theme].ogg`
  - Example: `music_town_day.ogg`, `music_dungeon_combat.ogg`

#### Area Themes
- **Town**:
  - `music_town_day.ogg` - Daytime town theme
  - `music_town_night.ogg` - Nighttime town theme
  - `music_town_festival.ogg` - Festival theme
  - `music_town_tavern.ogg` - Tavern theme

- **Wilderness**:
  - `music_forest_day.ogg` - Forest theme
  - `music_mountains.ogg` - Mountain theme
  - `music_desert.ogg` - Desert theme
  - `music_plains.ogg` - Plains theme

- **Dungeons**:
  - `music_dungeon_explore.ogg` - Dungeon exploration
  - `music_dungeon_combat.ogg` - Dungeon combat
  - `music_dungeon_boss.ogg` - Boss battle
  - `music_dungeon_treasure.ogg` - Treasure room

- **Special Areas**:
  - `music_castle.ogg` - Castle theme
  - `music_temple.ogg` - Temple theme
  - `music_ruins.ogg` - Ancient ruins
  - `music_crypt.ogg` - Crypt theme

#### Combat Themes
- **Regular Combat**:
  - `music_combat_normal.ogg` - Standard combat
  - `music_combat_intense.ogg` - Intense combat
  - `music_combat_victory.ogg` - Victory theme

- **Boss Battles**:
  - `music_boss_intro.ogg` - Boss introduction
  - `music_boss_phase1.ogg` - First phase
  - `music_boss_phase2.ogg` - Second phase
  - `music_boss_victory.ogg` - Boss victory

#### Event Themes
- **Story Events**:
  - `music_story_intro.ogg` - Introduction
  - `music_story_quest.ogg` - Quest theme
  - `music_story_revelation.ogg` - Story revelation
  - `music_story_ending.ogg` - Ending theme

- **Special Events**:
  - `music_event_celebration.ogg` - Celebration
  - `music_event_tragedy.ogg` - Tragedy
  - `music_event_mystery.ogg` - Mystery
  - `music_event_romance.ogg` - Romance

#### Music Notes
1. **Composition Guidelines**:
   - Use consistent instrumentation across themes
   - Maintain thematic motifs for continuity
   - Create smooth transitions between tracks
   - Consider dynamic music systems

2. **Technical Requirements**:
   - All tracks should be loopable
   - Include fade-in/fade-out points
   - Provide alternate versions for different intensities
   - Consider memory usage for mobile platforms

3. **Implementation Notes**:
   - Music should crossfade between areas
   - Combat music should transition smoothly
   - Ambient tracks should be seamless
   - Consider volume levels for different contexts

### Voice
- **Directory**: `assets/sounds/voice/`
- **Format**: OGG
- **Sample Rate**: 44.1kHz
- **Bit Depth**: 16-bit
- **Channels**: Mono
- **Naming Convention**: `voice_[character]_[emotion]_[text].ogg`
  - Example: `voice_merchant_happy_greeting.ogg`

#### NPC Voice Lines
- **Merchants**:
  - `voice_merchant_happy_greeting.ogg` - "Welcome to my shop!"
  - `voice_merchant_neutral_greeting.ogg` - "What can I do for you?"
  - `voice_merchant_sad_greeting.ogg` - "Business is slow today..."
  - `voice_merchant_happy_thanks.ogg` - "Thank you for your purchase!"
  - `voice_merchant_neutral_thanks.ogg` - "Come again soon."
  - `voice_merchant_sad_goodbye.ogg` - "I hope you find what you're looking for..."

- **Quest Givers**:
  - `voice_questgiver_happy_newquest.ogg` - "I have a task for you!"
  - `voice_questgiver_neutral_explain.ogg` - "Let me explain what needs to be done..."
  - `voice_questgiver_happy_complete.ogg` - "You've done well!"
  - `voice_questgiver_sad_fail.ogg` - "I'm disappointed..."
  - `voice_questgiver_neutral_reminder.ogg` - "Don't forget about our agreement..."

- **Innkeepers**:
  - `voice_innkeeper_happy_greeting.ogg` - "Welcome to our inn!"
  - `voice_innkeeper_neutral_room.ogg` - "Would you like a room?"
  - `voice_innkeeper_happy_food.ogg` - "Our special today is..."
  - `voice_innkeeper_sad_goodbye.ogg` - "Safe travels!"

- **Guards**:
  - `voice_guard_neutral_greeting.ogg` - "Halt! State your business."
  - `voice_guard_angry_warning.ogg` - "You're not welcome here!"
  - `voice_guard_happy_thanks.ogg` - "Thank you for your service."
  - `voice_guard_neutral_direction.ogg` - "The tavern is that way..."

#### Player Character Voice Lines
- **Combat**:
  - `voice_player_attack_1.ogg` - "Take this!"
  - `voice_player_attack_2.ogg` - "For glory!"
  - `voice_player_attack_3.ogg` - "En garde!"
  - `voice_player_hurt_1.ogg` - "Ugh!"
  - `voice_player_hurt_2.ogg` - "Argh!"
  - `voice_player_death.ogg` - "No...!"

- **Interaction**:
  - `voice_player_greet_1.ogg` - "Hello there!"
  - `voice_player_greet_2.ogg` - "Greetings!"
  - `voice_player_thanks_1.ogg` - "Thank you!"
  - `voice_player_thanks_2.ogg` - "Much appreciated!"
  - `voice_player_goodbye_1.ogg` - "Farewell!"
  - `voice_player_goodbye_2.ogg` - "Until next time!"

- **Emotional**:
  - `voice_player_happy_1.ogg` - "Excellent!"
  - `voice_player_happy_2.ogg` - "Perfect!"
  - `voice_player_sad_1.ogg` - "Oh no..."
  - `voice_player_sad_2.ogg` - "That's unfortunate..."
  - `voice_player_angry_1.ogg` - "How dare you!"
  - `voice_player_angry_2.ogg` - "You'll pay for that!"

#### Voice Line Notes
1. **Recording Guidelines**:
   - Use consistent microphone setup
   - Maintain consistent distance from microphone
   - Record in a quiet, controlled environment
   - Provide multiple takes of each line

2. **Emotional Range**:
   - Each line should have 2-3 emotional variants
   - Emotions: Happy, Neutral, Sad, Angry
   - Consider context-appropriate intensity

3. **Technical Requirements**:
   - Normalize all voice lines to -3dB
   - Remove background noise
   - Ensure consistent volume across all lines
   - Trim silence from start and end

4. **Implementation Notes**:
   - Voice lines should be triggered by specific events
   - Consider cooldown periods between repeated lines
   - Allow for volume adjustment in settings
   - Support muting individual voice types

## Animation Specifications

### Character Animations
- **Directory**: `assets/animations/characters/`
- **Format**: PNG sprite sheets
- **Frame Size**: 32x32 pixels
- **Frame Rate**: 12 FPS
- **Naming Convention**: `anim_[character]_[action].png`
  - Example: `anim_player_walk.png`
- **Layout**: Frames arranged horizontally
- **Frame Count**:
  - Idle: 4 frames
  - Walk: 4 frames
  - Attack: 4 frames
  - Death: 4 frames

### Effect Animations
- **Directory**: `assets/animations/effects/`
- **Format**: PNG sprite sheets
- **Frame Size**: 32x32 pixels
- **Frame Rate**: 12 FPS
- **Naming Convention**: `effect_[type]_[variant].png`
  - Example: `effect_explosion_small.png`

#### Combat Effects
- **Weapon Trails**:
  - `effect_sword_slash.png` - Sword swing trail (4 frames)
  - `effect_axe_swing.png` - Axe swing trail (4 frames)
  - `effect_bow_shot.png` - Arrow trail (4 frames)
  - `effect_magic_cast.png` - Magic casting effect (6 frames)

- **Impact Effects**:
  - `effect_hit_normal.png` - Normal hit impact (4 frames)
  - `effect_hit_critical.png` - Critical hit impact (6 frames)
  - `effect_hit_magic.png` - Magic hit impact (6 frames)
  - `effect_hit_poison.png` - Poison hit effect (8 frames)

- **Defense Effects**:
  - `effect_block_shield.png` - Shield block (4 frames)
  - `effect_dodge.png` - Dodge effect (4 frames)
  - `effect_parry.png` - Parry effect (4 frames)
  - `effect_counter.png` - Counter attack effect (6 frames)

#### Magic Effects
- **Elemental**:
  - `effect_fire_cast.png` - Fire spell cast (6 frames)
  - `effect_fire_impact.png` - Fire spell impact (8 frames)
  - `effect_ice_cast.png` - Ice spell cast (6 frames)
  - `effect_ice_impact.png` - Ice spell impact (8 frames)
  - `effect_lightning_cast.png` - Lightning spell cast (6 frames)
  - `effect_lightning_impact.png` - Lightning spell impact (8 frames)

- **Support**:
  - `effect_heal.png` - Healing effect (8 frames)
  - `effect_buff.png` - Buff effect (8 frames)
  - `effect_debuff.png` - Debuff effect (8 frames)
  - `effect_teleport.png` - Teleport effect (8 frames)

#### Environment Effects
- **Weather**:
  - `effect_rain.png` - Rain drops (8 frames)
  - `effect_snow.png` - Snow flakes (8 frames)
  - `effect_wind.png` - Wind gusts (8 frames)
  - `effect_lightning.png` - Lightning strike (6 frames)

- **Ambient**:
  - `effect_torch_flicker.png` - Torch flame (8 frames)
  - `effect_campfire.png` - Campfire (8 frames)
  - `effect_water_ripple.png` - Water ripple (8 frames)
  - `effect_fog.png` - Fog effect (8 frames)

#### UI Effects
- **Notifications**:
  - `effect_quest_complete.png` - Quest completion (8 frames)
  - `effect_level_up.png` - Level up (8 frames)
  - `effect_item_found.png` - Item found (8 frames)
  - `effect_achievement.png` - Achievement unlocked (8 frames)

- **Menu Effects**:
  - `effect_menu_select.png` - Menu selection (4 frames)
  - `effect_menu_confirm.png` - Menu confirmation (4 frames)
  - `effect_menu_cancel.png` - Menu cancellation (4 frames)
  - `effect_menu_transition.png` - Menu transition (8 frames)

#### Effect Animation Notes
1. **Frame Requirements**:
   - Combat effects: 4-6 frames
   - Magic effects: 6-8 frames
   - Environmental effects: 8 frames
   - UI effects: 4-8 frames

2. **Animation Guidelines**:
   - Maintain consistent frame timing
   - Use smooth transitions between frames
   - Consider particle effects for complex animations
   - Ensure effects are visible against all backgrounds

3. **Technical Requirements**:
   - All frames must be the same size
   - Use transparency for non-rectangular effects
   - Optimize sprite sheets for performance
   - Consider memory usage for mobile platforms

4. **Implementation Notes**:
   - Effects should be triggered by specific events
   - Consider layering multiple effects
   - Allow for effect scaling
   - Support effect customization

### UI Animations
- **Directory**: `assets/animations/ui/`
- **Format**: PNG sprite sheets
- **Frame Size**: Varies by element
- **Frame Rate**: 12 FPS
- **Naming Convention**: `ui_anim_[element]_[state].png`
  - Example: `ui_anim_button_press.png`

#### Button Animations
- **Standard Buttons**:
  - `ui_anim_button_idle.png` - Idle state (4 frames)
  - `ui_anim_button_hover.png` - Hover state (4 frames)
  - `ui_anim_button_press.png` - Press state (4 frames)
  - `ui_anim_button_disabled.png` - Disabled state (4 frames)

- **Special Buttons**:
  - `ui_anim_button_quest.png` - Quest button (8 frames)
  - `ui_anim_button_inventory.png` - Inventory button (8 frames)
  - `ui_anim_button_character.png` - Character button (8 frames)
  - `ui_anim_button_settings.png` - Settings button (8 frames)

#### Menu Animations
- **Transitions**:
  - `ui_anim_menu_open.png` - Menu opening (8 frames)
  - `ui_anim_menu_close.png` - Menu closing (8 frames)
  - `ui_anim_menu_transition.png` - Menu transition (8 frames)
  - `ui_anim_submenu_open.png` - Submenu opening (6 frames)
  - `ui_anim_submenu_close.png` - Submenu closing (6 frames)

- **Navigation**:
  - `ui_anim_menu_select.png` - Selection highlight (4 frames)
  - `ui_anim_menu_scroll.png` - Scrolling effect (4 frames)
  - `ui_anim_menu_tab.png` - Tab switching (4 frames)
  - `ui_anim_menu_back.png` - Back button (4 frames)

#### Inventory Animations
- **Item Interactions**:
  - `ui_anim_item_pickup.png` - Item pickup (8 frames)
  - `ui_anim_item_drop.png` - Item drop (8 frames)
  - `ui_anim_item_equip.png` - Item equip (8 frames)
  - `ui_anim_item_unequip.png` - Item unequip (8 frames)
  - `ui_anim_item_use.png` - Item use (8 frames)

- **Inventory States**:
  - `ui_anim_inventory_open.png` - Inventory opening (8 frames)
  - `ui_anim_inventory_close.png` - Inventory closing (8 frames)
  - `ui_anim_inventory_sort.png` - Inventory sorting (8 frames)
  - `ui_anim_inventory_filter.png` - Filter application (8 frames)

#### Quest UI Animations
- **Quest States**:
  - `ui_anim_quest_new.png` - New quest notification (8 frames)
  - `ui_anim_quest_update.png` - Quest update (8 frames)
  - `ui_anim_quest_complete.png` - Quest completion (8 frames)
  - `ui_anim_quest_fail.png` - Quest failure (8 frames)

- **Quest Navigation**:
  - `ui_anim_quest_select.png` - Quest selection (4 frames)
  - `ui_anim_quest_track.png` - Quest tracking toggle (4 frames)
  - `ui_anim_quest_reward.png` - Reward display (8 frames)
  - `ui_anim_quest_objective.png` - Objective update (4 frames)

#### Character UI Animations
- **Stats Display**:
  - `ui_anim_stat_increase.png` - Stat increase (8 frames)
  - `ui_anim_stat_decrease.png` - Stat decrease (8 frames)
  - `ui_anim_level_up.png` - Level up celebration (12 frames)
  - `ui_anim_skill_learn.png` - Skill learned (8 frames)

- **Equipment**:
  - `ui_anim_equip_slot.png` - Equipment slot highlight (4 frames)
  - `ui_anim_equip_change.png` - Equipment change (8 frames)
  - `ui_anim_equip_compare.png` - Equipment comparison (4 frames)
  - `ui_anim_equip_preview.png` - Equipment preview (4 frames)

#### UI Animation Notes
1. **Frame Requirements**:
   - Button animations: 4 frames
   - Menu transitions: 6-8 frames
   - State changes: 8 frames
   - Special effects: 8-12 frames

2. **Animation Guidelines**:
   - Keep animations subtle and non-distracting
   - Ensure smooth transitions between states
   - Maintain consistent timing across all UI elements
   - Consider performance impact of complex animations

3. **Technical Requirements**:
   - Optimize sprite sheets for performance
   - Use transparency for non-rectangular elements
   - Consider memory usage for mobile platforms
   - Support animation speed adjustment

4. **Implementation Notes**:
   - Animations should be interruptible
   - Consider layering multiple animations
   - Allow for animation skipping
   - Support animation disabling in settings

## Asset Creation Guidelines

1. **Color Palette**:
   - Use a consistent color palette across all assets
   - Limit colors to 16-bit (65,536 colors)
   - Use transparency for non-rectangular elements

2. **Style Consistency**:
   - Maintain consistent art style across all assets
   - Use similar shading techniques
   - Keep proportions consistent

3. **Performance Considerations**:
   - Optimize image sizes
   - Use sprite sheets for animations
   - Compress audio files appropriately
   - Consider memory usage for mobile platforms

4. **Accessibility**:
   - Ensure sufficient contrast for UI elements
   - Provide alternative text for important visual elements
   - Consider colorblind-friendly palettes

## Asset Integration

To add new assets:

1. Place the asset in the appropriate directory
2. Follow the naming conventions
3. Ensure the asset meets the specified requirements
4. Update the asset loading code if necessary
5. Test the asset in-game

## Asset Management

- Keep a backup of all original asset files
- Maintain a version control system for assets
- Document any changes or updates to assets
- Keep a record of asset sources and licenses 