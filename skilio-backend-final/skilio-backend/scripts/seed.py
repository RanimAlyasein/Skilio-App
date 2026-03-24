"""
scripts/seed.py
────────────────
Full database seed for Skilio.

Creates:
  - 1 demo parent  (demo@skilio.com / Demo1234!)
  - 2 children     (Elif age 8, Kerem age 11)
  - 3 SkillModules (Outer Space, Deep Sea, Enchanted Forest)
  - 6 Lessons with full branching scenario graphs matching the kids UI
  - 5 Badges

Run after `alembic upgrade head`:
    python scripts/seed.py
Safe to re-run — skips records that already exist.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, check_db_connection
from app.core.security import hash_password
from app.models.badge import Badge, BadgeTriggerType
from app.models.child import Child
from app.models.lesson import Lesson
from app.models.module import SkillModule
from app.models.scenario import NodeType, ScenarioChoice, ScenarioNode
from app.models.user import User


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_or_create(db, model, filter_kw: dict, create_kw: dict = None):
    obj = db.query(model).filter_by(**filter_kw).first()
    if obj:
        return obj, False
    obj = model(**(create_kw or filter_kw))
    db.add(obj); db.flush()
    return obj, True

def log(created, label):
    print(f"  {'+ created' if created else '· exists '}: {label}")

def mk_node(db, lesson_id, content, ntype, correct=False):
    n = ScenarioNode(lesson_id=lesson_id, content_text=content,
                     node_type=ntype, is_correct_path=correct)
    db.add(n); db.flush(); return n

def mk_choice(db, node_id, text, next_id, safe=False, feedback=None, idx=0):
    c = ScenarioChoice(node_id=node_id, choice_text=text, next_node_id=next_id,
                       is_safe_choice=safe, feedback_text=feedback, order_index=idx)
    db.add(c); db.flush(); return c


# ── Users & Children ──────────────────────────────────────────────────────────

def seed_users(db):
    print("\n[Users]")
    parent, created = get_or_create(
        db, User, {"email": "demo@skilio.com"},
        {"email": "demo@skilio.com", "full_name": "Demo Parent",
         "hashed_password": hash_password("Demo1234!"), "is_active": True},
    )
    log(created, "demo@skilio.com  /  Demo1234!")
    return parent

def seed_children(db, parent):
    print("\n[Children]")
    elif_c, c1 = get_or_create(
        db, Child, {"parent_id": parent.id, "display_name": "Elif"},
        {"parent_id": parent.id, "display_name": "Elif",
         "age": 8, "total_xp": 0, "is_active": True},
    )
    log(c1, "Elif, age 8")
    kerem, c2 = get_or_create(
        db, Child, {"parent_id": parent.id, "display_name": "Kerem"},
        {"parent_id": parent.id, "display_name": "Kerem",
         "age": 11, "total_xp": 0, "is_active": True},
    )
    log(c2, "Kerem, age 11")
    return elif_c, kerem


# ── Modules ───────────────────────────────────────────────────────────────────

def seed_modules(db):
    print("\n[Skill Modules]")
    space, c1 = get_or_create(
        db, SkillModule, {"title": "Outer Space"},
        {"title": "Outer Space",
         "description": "Mars, Jupiter and the Moon need your help! Make smart choices to save the solar system and learn how to stay safe.",
         "age_min": 5, "age_max": 12, "is_published": True, "order_index": 1},
    )
    log(c1, "Outer Space")

    sea, c2 = get_or_create(
        db, SkillModule, {"title": "The Deep Sea"},
        {"title": "The Deep Sea",
         "description": "Splash the Dolphin needs help — his friends are missing and a storm is coming. Learn who to trust and when to ask for help.",
         "age_min": 6, "age_max": 14, "is_published": True, "order_index": 2},
    )
    log(c2, "The Deep Sea")

    forest, c3 = get_or_create(
        db, SkillModule, {"title": "Enchanted Forest"},
        {"title": "Enchanted Forest",
         "description": "Leo, Foxy and Ollie need your wisdom. Navigate shortcuts, fire safety and keeping secrets — and learn what a real hero does.",
         "age_min": 7, "age_max": 15, "is_published": True, "order_index": 3},
    )
    log(c3, "Enchanted Forest")
    return space, sea, forest


# ── OUTER SPACE — Lesson 1: Mars Needs Help! ─────────────────────────────────
#
#  START: Mars separated from solar system, two paths home
#  ─ safe   → BRANCH: Asteroid following, stop at Space Station?
#              ─ safe   → END (correct): Space Rangers help, mission complete
#              └ unsafe → END (wrong):   Try alone, danger but teachable
#  └ unsafe → END (wrong): Dark Nebula shortcut, gets lost

def seed_mars(db, module):
    lesson, created = get_or_create(
        db, Lesson, {"module_id": module.id, "title": "Mars Needs Help!"},
        {"module_id": module.id, "title": "Mars Needs Help!",
         "description": "Mars got separated during a meteor shower! Help him choose the safe path home.",
         "xp_reward": 60, "order_index": 1},
    )
    log(created, "Lesson: Mars Needs Help!")
    if not created and lesson.entry_node_id:
        return lesson

    n1 = mk_node(db, lesson.id,
        "I'm Mars and I got separated from the solar system during a meteor shower! "
        "I found two paths home. The first is the official Space Highway — a bit longer "
        "but safe and well-lit with Space Rangers patrolling. The second is a shortcut "
        "through the Dark Nebula — much faster, but nobody goes there and strange things "
        "happen inside. What should I do?",
        NodeType.START)

    n2 = mk_node(db, lesson.id,
        "Good choice! I'm on the Space Highway but a strange glowing asteroid is "
        "following me. I could try to outrun it alone — or I could stop at the Space "
        "Station ahead and ask the Space Rangers for help. What do I do?",
        NodeType.BRANCH)

    n3 = mk_node(db, lesson.id,
        "Oh no… the Dark Nebula was full of gravity traps! But it's okay — I sent "
        "a distress signal and the Space Rangers found me. I learned my lesson: "
        "safe and familiar routes are always better than risky shortcuts, even if "
        "they take longer. Safe paths + trusted helpers = always the right choice! +20 XP",
        NodeType.END, correct=False)

    n4 = mk_node(db, lesson.id,
        "YOU DID IT! 🌟 Mars made it home safely! The Space Rangers stopped the "
        "asteroid AND found two lost space probes along the way. Because you chose "
        "safe paths and asked for help, everyone in the solar system is safer today. "
        "I'm shining extra bright just for you! ⭐ +60 XP",
        NodeType.END, correct=True)

    n5 = mk_node(db, lesson.id,
        "Trying to outrun the asteroid alone was too dangerous — but the Space "
        "Rangers saw what happened and swooped in to help! Real heroes know when "
        "to ask for help. Trusted adults and authorities are there for exactly this. +20 XP",
        NodeType.END, correct=False)

    mk_choice(db, n1.id, "Take the safe Space Highway home even though it takes longer",
              next_id=n2.id, safe=True,
              feedback="Excellent! Safe and familiar routes are always the smartest choice.", idx=0)
    mk_choice(db, n1.id, "Take the shortcut through the Dark Nebula to get home faster",
              next_id=n3.id, safe=False,
              feedback="Unknown shortcuts can be very dangerous — always choose the safe path!", idx=1)

    mk_choice(db, n2.id, "Stop at the Space Station and ask the Space Rangers for help",
              next_id=n4.id, safe=True,
              feedback="Asking trusted authorities for help is always the right move!", idx=0)
    mk_choice(db, n2.id, "Try to outrun the asteroid alone — it'll be an adventure!",
              next_id=n5.id, safe=False,
              feedback="Going alone against danger is never a good idea. Real heroes ask for help!", idx=1)

    lesson.entry_node_id = n1.id
    db.add(lesson); db.flush()
    return lesson


# ── OUTER SPACE — Lesson 2: The Moon's Warning ───────────────────────────────

def seed_moon(db, module):
    lesson, created = get_or_create(
        db, Lesson, {"module_id": module.id, "title": "The Moon's Warning"},
        {"module_id": module.id, "title": "The Moon's Warning",
         "description": "The Moon spotted a dangerous asteroid heading for Earth! Who do you tell — and how fast?",
         "xp_reward": 70, "order_index": 2},
    )
    log(created, "Lesson: The Moon's Warning")
    if not created and lesson.entry_node_id:
        return lesson

    n1 = mk_node(db, lesson.id,
        "Psst! I'm the Moon, and I can see everything from up here. I just spotted "
        "something scary — a giant asteroid is heading toward Earth and I only have "
        "a few minutes! I could tell the Sun who can warn everyone immediately, or I "
        "could try to push the asteroid away by myself. What should I do?",
        NodeType.START)

    n2 = mk_node(db, lesson.id,
        "The Sun warned everyone in time! Now the scientists need to know what to do "
        "when YOU see something dangerous. If you spot a fire, a stranger acting "
        "strangely, or an emergency — what do you do FIRST?",
        NodeType.BRANCH)

    n3 = mk_node(db, lesson.id,
        "Trying to handle a giant asteroid alone didn't work — but I sent the warning "
        "just in time! Big dangers need trusted adults who have the power, experience, "
        "and resources to fix things we can't fix alone. Always tell someone! +20 XP",
        NodeType.END, correct=False)

    n4 = mk_node(db, lesson.id,
        "Earth is SAFE! 🌍 The scientists redirected the asteroid just in time! "
        "You proved that telling trusted people about dangers quickly — instead of "
        "keeping secrets or trying alone — keeps everyone safe. Sleep well, little hero! ✨ +70 XP",
        NodeType.END, correct=True)

    n5 = mk_node(db, lesson.id,
        "Friends are great, but for real emergencies they often can't actually fix "
        "the problem. Trusted adults — parents, teachers, police — have the power "
        "and resources to help. Always go to a grown-up in an emergency! +20 XP",
        NodeType.END, correct=False)

    mk_choice(db, n1.id, "Tell the Sun immediately — this is too big to handle alone",
              next_id=n2.id, safe=True,
              feedback="Telling a trusted authority about dangers is always the right call!", idx=0)
    mk_choice(db, n1.id, "Try to push the asteroid away by myself without telling anyone",
              next_id=n3.id, safe=False,
              feedback="Some dangers are too big to handle alone — always tell a trusted adult!", idx=1)

    mk_choice(db, n2.id, "Find a trusted adult and tell them clearly what I saw",
              next_id=n4.id, safe=True,
              feedback="YES! Parents, teachers, police. Tell them clearly and fast!", idx=0)
    mk_choice(db, n2.id, "Tell my friends first and figure it out together",
              next_id=n5.id, safe=False,
              feedback="Friends are great, but for real dangers adults have the power to help!", idx=1)

    lesson.entry_node_id = n1.id
    db.add(lesson); db.flush()
    return lesson


# ── DEEP SEA — Lesson 1: Lost Whale Baby ────────────────────────────────────

def seed_whale(db, module):
    lesson, created = get_or_create(
        db, Lesson, {"module_id": module.id, "title": "Lost Whale Baby"},
        {"module_id": module.id, "title": "Lost Whale Baby",
         "description": "A baby whale is lost and crying! Do you call the Coastguard or jump in alone?",
         "xp_reward": 65, "order_index": 1},
    )
    log(created, "Lesson: Lost Whale Baby")
    if not created and lesson.entry_node_id:
        return lesson

    n1 = mk_node(db, lesson.id,
        "MMMM! (That means I'm crying.) I'm Baby Whale and I swam too far from "
        "my mum — now I'm lost in the deep dark water! I see a child on a boat — "
        "that's you! Should you jump in the water to help me yourself, or call the "
        "Coastguard on the radio?",
        NodeType.START)

    n2 = mk_node(db, lesson.id,
        "The Coastguard is on the way! But now a fish I've never seen before says "
        "he knows a shortcut to find Baby Whale's mum. He wants you to follow him "
        "into a dark underwater cave. Should you go?",
        NodeType.BRANCH)

    n3 = mk_node(db, lesson.id,
        "Even good swimmers can get into serious trouble in the open ocean. The "
        "Coastguard arrived and helped safely! In real emergencies at sea, always "
        "contact official helpers — they have boats, trained rescuers, and the right "
        "equipment. You can't always fix things alone! +20 XP",
        NodeType.END, correct=False)

    n4 = mk_node(db, lesson.id,
        "MOOOOOO! (That's whale for THANK YOU!) 💙 Baby Whale is back with his mum! "
        "You were so wise to call the Coastguard AND refuse to follow a stranger into "
        "an unknown place. Real heroes know when to ask for help — and that's the "
        "bravest thing of all! +65 XP",
        NodeType.END, correct=True)

    n5 = mk_node(db, lesson.id,
        "Following unknown animals into dark unknown places is very dangerous! "
        "The Coastguard found us luckily. Remember: never follow strangers into "
        "unknown places, even if they seem friendly and helpful. Stay safe! +20 XP",
        NodeType.END, correct=False)

    mk_choice(db, n1.id, "Call the Coastguard on the radio — they have proper equipment to help",
              next_id=n2.id, safe=True,
              feedback="Perfect! Never jump into dangerous water alone. Always get qualified help!", idx=0)
    mk_choice(db, n1.id, "Jump in the water to guide Baby Whale back yourself",
              next_id=n3.id, safe=False,
              feedback="Even good swimmers can get into trouble in open ocean. Call for help first!", idx=1)

    mk_choice(db, n2.id, "Wait for the Coastguard — don't follow unknown fish into dark caves",
              next_id=n4.id, safe=True,
              feedback="Never follow strangers into unknown places, even if they seem helpful!", idx=0)
    mk_choice(db, n2.id, "Follow the fish — maybe he really does know the way",
              next_id=n5.id, safe=False,
              feedback="Unknown places with unknown guides can be very dangerous!", idx=1)

    lesson.entry_node_id = n1.id
    db.add(lesson); db.flush()
    return lesson


# ── DEEP SEA — Lesson 2: The Friendly Shark ─────────────────────────────────

def seed_shark(db, module):
    lesson, created = get_or_create(
        db, Lesson, {"module_id": module.id, "title": "The Friendly Shark"},
        {"module_id": module.id, "title": "The Friendly Shark",
         "description": "A shark says he's friendly and wants to be your guide. Can you trust him?",
         "xp_reward": 70, "order_index": 2},
    )
    log(created, "Lesson: The Friendly Shark")
    if not created and lesson.entry_node_id:
        return lesson

    n1 = mk_node(db, lesson.id,
        "You're swimming with Splash the Dolphin when a large shark swims up. "
        "'Don't be scared!' he says. 'I know a secret shortcut to the treasure reef! "
        "It's just the two of us — don't tell Splash. Come with me!' "
        "What do you do?",
        NodeType.START)

    n2 = mk_node(db, lesson.id,
        "You told Splash immediately and he said 'Good thinking! I don't know that "
        "shark and we should NEVER keep secrets from trusted friends. Let's find the "
        "treasure reef together on the safe route!' Now Splash asks: if someone "
        "asks you to keep a secret from a parent or trusted adult, what should you do?",
        NodeType.BRANCH)

    n3 = mk_node(db, lesson.id,
        "Going alone with someone you don't know — especially when they ask you to "
        "keep it secret — is very unsafe. Splash came looking for you and found you "
        "in time! Remember: when someone asks you to go somewhere secretly without "
        "telling trusted adults, that is a danger sign. Always tell someone! +20 XP",
        NodeType.END, correct=False)

    n4 = mk_node(db, lesson.id,
        "Exactly right! Secrets that make you feel uncomfortable or that a grown-up "
        "asks you to keep from your parents are NEVER okay. Safe adults don't ask "
        "children to keep those kinds of secrets. You and Splash found the treasure "
        "reef together — the safe way! ✨ +70 XP",
        NodeType.END, correct=True)

    n5 = mk_node(db, lesson.id,
        "Keeping secret requests from trusted adults is never safe. Good secrets "
        "are things like surprise birthday parties. Bad secrets make you feel "
        "uncomfortable or scared — those must always be told to a trusted adult. "
        "Splash helped you understand! +20 XP",
        NodeType.END, correct=False)

    mk_choice(db, n1.id, "Say no and immediately tell Splash what the shark asked",
              next_id=n2.id, safe=True,
              feedback="Always tell a trusted friend or adult when someone asks you to keep unsafe secrets!", idx=0)
    mk_choice(db, n1.id, "Follow the shark alone without telling Splash",
              next_id=n3.id, safe=False,
              feedback="Going alone secretly with someone you don't know is very dangerous!", idx=1)

    mk_choice(db, n2.id, "Always tell a trusted adult — secrets that make you uncomfortable are never okay",
              next_id=n4.id, safe=True,
              feedback="Exactly! Safe adults never ask children to keep secrets from parents.", idx=0)
    mk_choice(db, n2.id, "Keep it — they said to keep it secret so I should",
              next_id=n5.id, safe=False,
              feedback="Unsafe secrets must always be told to a trusted adult — never keep them!", idx=1)

    lesson.entry_node_id = n1.id
    db.add(lesson); db.flush()
    return lesson


# ── ENCHANTED FOREST — Lesson 1: Foxy's Shortcut ────────────────────────────

def seed_foxy(db, module):
    lesson, created = get_or_create(
        db, Lesson, {"module_id": module.id, "title": "Foxy's Shortcut"},
        {"module_id": module.id, "title": "Foxy's Shortcut",
         "description": "Foxy offers a shortcut through the Dark Hollow. Leo says use the safe road. Who do you follow?",
         "xp_reward": 70, "order_index": 1},
    )
    log(created, "Lesson: Foxy's Shortcut")
    if not created and lesson.entry_node_id:
        return lesson

    n1 = mk_node(db, lesson.id,
        "Psst, hey you! It's me, Foxy! I know a shortcut through the Dark Hollow — "
        "nobody goes there but I promise it's totally fine! Leo the Lion says everyone "
        "must take the Long Light Path back to the village, but that takes twice as long. "
        "Come on, the Dark Hollow will be an adventure! What do you do?",
        NodeType.START)

    n2 = mk_node(db, lesson.id,
        "Great choice! But now it's getting dark and I see two bridges ahead. The "
        "old stone bridge has been safe for 100 years. The new wooden bridge looks "
        "fine but nobody has actually tested it yet. We need to cross — which do you choose?",
        NodeType.BRANCH)

    n3 = mk_node(db, lesson.id,
        "Even I got confused in the Dark Hollow — I never actually knew the way! "
        "I just wanted company. Leo found us luckily. Remember: when someone offers "
        "a shortcut that trusted adults wouldn't approve of, always say no and "
        "stick to the known safe path. +20 XP",
        NodeType.END, correct=False)

    n4 = mk_node(db, lesson.id,
        "You made it home safely! 🎉 You passed the Forest Safety Test! Every day "
        "people will offer shortcuts that seem easier. But real smart adventurers know "
        "that trusted routes and trusted guides are always worth it. "
        "ROAAAAAR! (Leo's happy roar!) +70 XP",
        NodeType.END, correct=True)

    n5 = mk_node(db, lesson.id,
        "'Looks fine' isn't the same as 'is safe'! The new bridge collapsed partway "
        "across — but a tree branch saved us. Untested paths carry unknown risks. "
        "When in doubt, always choose the proven safe option. +20 XP",
        NodeType.END, correct=False)

    mk_choice(db, n1.id, "Follow Leo's Long Light Path — the trusted guardian knows best",
              next_id=n2.id, safe=True,
              feedback="Always trust the adult guardian over an unfamiliar shortcut offer!", idx=0)
    mk_choice(db, n1.id, "Follow Foxy through the Dark Hollow — he sounds confident",
              next_id=n3.id, safe=False,
              feedback="Unknown shortcuts offered by people you just met can lead to danger!", idx=1)

    mk_choice(db, n2.id, "Take the old tested stone bridge — proven safe is worth the extra steps",
              next_id=n4.id, safe=True,
              feedback="Wise! Always stick to what is known to be safe.", idx=0)
    mk_choice(db, n2.id, "Try the new wooden bridge — it looks fine to me",
              next_id=n5.id, safe=False,
              feedback="'Looks fine' is not the same as 'is safe'! Untested paths carry unknown risks.", idx=1)

    lesson.entry_node_id = n1.id
    db.add(lesson); db.flush()
    return lesson


# ── ENCHANTED FOREST — Lesson 2: Ollie Sees Smoke! ──────────────────────────

def seed_ollie(db, module):
    lesson, created = get_or_create(
        db, Lesson, {"module_id": module.id, "title": "Ollie Sees Smoke!"},
        {"module_id": module.id, "title": "Ollie Sees Smoke!",
         "description": "Wise Ollie spotted smoke near the old oak tree! What do you do — and how fast?",
         "xp_reward": 75, "order_index": 2},
    )
    log(created, "Lesson: Ollie Sees Smoke!")
    if not created and lesson.entry_node_id:
        return lesson

    n1 = mk_node(db, lesson.id,
        "Hoo hoo! I'm Ollie the Owl and I can see EVERYTHING from my tree. "
        "I just spotted smoke near the old oak — this could be a fire starting! "
        "I could: try to fan out the smoke myself with my wings, wake up the "
        "Forest Elder right away, or wait to see if it gets bigger first. What should I do?",
        NodeType.START)

    n2 = mk_node(db, lesson.id,
        "The Forest Elder is awake! Animals are scared and running in different "
        "directions. Leo says: 'Everyone get LOW under the smoke and follow the "
        "marked green path to the clearing! Do NOT run back into the trees!' "
        "But some animals want to go back to get their things. What do you say?",
        NodeType.BRANCH)

    n3 = mk_node(db, lesson.id,
        "Fires spread faster than any animal in the forest! I should have told "
        "the Elder straight away. The Rangers put it out quickly once they knew. "
        "Rule number one: NEVER wait when you see smoke or fire. Tell a trusted "
        "adult IMMEDIATELY — every second matters. +20 XP",
        NodeType.END, correct=False)

    n4 = mk_node(db, lesson.id,
        "HOO HOO HOO! Everyone is safe! The Forest Rangers put out the fire "
        "quickly because you alerted the Elder so fast. You made three perfect "
        "choices: told an adult IMMEDIATELY, didn't try alone, and helped "
        "others reach safety. You have the heart of a hero! 🦉 +75 XP",
        NodeType.END, correct=True)

    n5 = mk_node(db, lesson.id,
        "In fire emergencies, we NEVER go back for things — objects can be "
        "replaced, lives cannot! Thankfully the Rangers arrived in time. "
        "Remember: GET OUT first, STAY OUT, then call for help from outside. "
        "Things can always be replaced. People cannot. +20 XP",
        NodeType.END, correct=False)

    mk_choice(db, n1.id, "Wake up the Forest Elder immediately — adults handle fire emergencies",
              next_id=n2.id, safe=True,
              feedback="Fire emergencies need adult help IMMEDIATELY. Never wait!", idx=0)
    mk_choice(db, n1.id, "Wait and watch to see if the smoke gets bigger first",
              next_id=n3.id, safe=False,
              feedback="Fires spread incredibly fast! Never wait when you see smoke. Tell an adult NOW!", idx=1)

    mk_choice(db, n2.id, "'No! We follow Leo's path NOW — things can be replaced, lives cannot!'",
              next_id=n4.id, safe=True,
              feedback="In fire: GET OUT and stay out. Objects can be replaced. Lives cannot!", idx=0)
    mk_choice(db, n2.id, "Help them quickly grab their things — it will only take a second",
              next_id=n5.id, safe=False,
              feedback="In emergencies, never go back for things! Every second counts.", idx=1)

    lesson.entry_node_id = n1.id
    db.add(lesson); db.flush()
    return lesson


# ── Badges ────────────────────────────────────────────────────────────────────

def seed_badges(db):
    print("\n[Badges]")
    badges = [
        ("First Step",           "Complete your very first lesson. Every hero starts somewhere!",
         BadgeTriggerType.FIRST_LESSON,   1,   10),
        ("Safety Explorer",      "Complete 3 different lessons. You're building real skills!",
         BadgeTriggerType.LESSON_COUNT,   3,   25),
        ("World Champion",       "Complete all lessons in a module. You're an expert!",
         BadgeTriggerType.MODULE_COMPLETE, 1,  50),
        ("XP Pioneer",           "Earn 100 XP total. You're on your way!",
         BadgeTriggerType.XP_MILESTONE,   100, 15),
        ("Safe Choice Champion", "Make 10 safe choices across all your lessons.",
         BadgeTriggerType.SAFE_CHOICES,   10,  30),
    ]
    for name, desc, trigger, value, bonus in badges:
        badge, created = get_or_create(
            db, Badge, {"name": name},
            {"name": name, "description": desc, "trigger_type": trigger,
             "trigger_value": value, "xp_bonus": bonus, "is_active": True},
        )
        log(created, f"Badge: {name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Skilio — database seed")
    print("=" * 60)
    check_db_connection()
    print("  Database OK\n")

    db = SessionLocal()
    try:
        parent = seed_users(db)
        seed_children(db, parent)

        space, sea, forest = seed_modules(db)

        print("\n[Lessons & Scenarios]")
        # Outer Space
        l1 = seed_mars(db, space)
        l2 = seed_moon(db, space)
        # Deep Sea
        l3 = seed_whale(db, sea)
        l4 = seed_shark(db, sea)
        # Enchanted Forest
        l5 = seed_foxy(db, forest)
        l6 = seed_ollie(db, forest)

        seed_badges(db)
        db.commit()

        print("\n" + "=" * 60)
        print("  Seed complete!")
        print("=" * 60)
        print(f"\n  Login:  demo@skilio.com  /  Demo1234!")
        print(f"\n  Modules & Lessons:")
        print(f"    🌌 Outer Space  (id={space.id})")
        print(f"       – Mars Needs Help!     lesson={l1.id}  entry_node={l1.entry_node_id}")
        print(f"       – The Moon's Warning   lesson={l2.id}  entry_node={l2.entry_node_id}")
        print(f"    🌊 The Deep Sea  (id={sea.id})")
        print(f"       – Lost Whale Baby       lesson={l3.id}  entry_node={l3.entry_node_id}")
        print(f"       – The Friendly Shark    lesson={l4.id}  entry_node={l4.entry_node_id}")
        print(f"    🌲 Enchanted Forest  (id={forest.id})")
        print(f"       – Foxy's Shortcut       lesson={l5.id}  entry_node={l5.entry_node_id}")
        print(f"       – Ollie Sees Smoke!     lesson={l6.id}  entry_node={l6.entry_node_id}")
        print(f"\n  Swagger: http://localhost:8000/docs\n")

    except Exception as exc:
        db.rollback()
        print(f"\n  [ERROR] Seed failed: {exc}")
        import traceback; traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
