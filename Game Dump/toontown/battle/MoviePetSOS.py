# File: M (Python 2.2)

from direct.interval.IntervalGlobal import *
from BattleProps import *
from BattleSounds import *
from direct.directnotify import DirectNotifyGlobal
import MovieCamera
import whrandom
import MovieUtil
import BattleParticles
import HealJokes
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.pets import Pet
notify = DirectNotifyGlobal.directNotify.newCategory('MoviePetSOS')
soundFiles = ('AA_heal_tickle.mp3', 'AA_heal_telljoke.mp3', 'AA_heal_smooch.mp3', 'AA_heal_happydance.mp3', 'AA_heal_pixiedust.mp3', 'AA_heal_juggle.mp3')
offset = Point3(0, 4.0, 0)

def doPetSOSs(PetSOSs):
    if len(PetSOSs) == 0:
        return (None, None)
    
    track = Sequence()
    textTrack = Sequence()
    for p in PetSOSs:
        ival = __doPetSOS(p)
        if ival:
            track.append(ival)
        
    
    camDuration = track.getDuration()
    camTrack = MovieCamera.chooseHealShot(PetSOSs, camDuration)
    return (track, camTrack)


def __doPetSOS(sos):
    return __healJuggle(sos)


def __healToon(toon, hp, ineffective = 0):
    notify.debug('healToon() - toon: %d hp: %d ineffective: %d' % (toon.doId, hp, ineffective))
    if ineffective == 1:
        laughter = whrandom.choice(TTLocalizer.MovieHealLaughterMisses)
    else:
        maxDam = ToontownBattleGlobals.AvPropDamage[0][1][0][1]
        if hp >= maxDam - 1:
            laughter = whrandom.choice(TTLocalizer.MovieHealLaughterHits2)
        else:
            laughter = whrandom.choice(TTLocalizer.MovieHealLaughterHits1)
    toon.setChatAbsolute(laughter, CFSpeech | CFTimeout)
    if hp > 0 and toon.hp != None:
        toon.setHp(min(toon.maxHp, toon.hp + hp), checkDied = 0)
    else:
        notify.debug('__healToon() - toon: %d hp: %d' % (toon.doId, hp))


def __teleportIn(attack, pet, pos = Point3(0, 0, 0), hpr = Vec3(180.0, 0.0, 0.0)):
    a = Func(pet.reparentTo, attack['battle'])
    b = Func(pet.setPos, pos)
    c = Func(pet.setHpr, hpr)
    d = Func(pet.addActive)
    e = Func(pet.loop, 'neutral')
    f = Wait(1.0)
    return Sequence(a, b, c, d, e, f)


def __teleportOut(attack, pet):
    a = Wait(1.0)
    b = Func(pet.removeActive)
    c = Func(pet.reparentTo, hidden)
    return Sequence(a, b, c)


def __doPet(attack, level, hp):
    track = __doSprinkle(attack, 'suits', hp)
    pbpText = attack['playByPlayText']
    pbpTrack = pbpText.getShowInterval(TTLocalizer.MovieNPCSOSCogsMiss, track.getDuration())
    return (track, pbpTrack)


def __healJuggle(heal):
    petProxyId = heal['petId']
    pet = Pet.Pet()
    if base.cr.doId2do.has_key(petProxyId):
        petProxy = base.cr.doId2do[petProxyId]
        if petProxy == None:
            return None
        
        pet.setDNA(petProxy.style)
        pet.setName(petProxy.petName)
    else:
        pet.setDNA([
            -1,
            0,
            0,
            -1,
            2,
            0,
            4,
            0,
            1])
        pet.setName('Smiley')
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    track = Sequence(__teleportIn(heal, pet))
    delay = 4.0
    first = 1
    targetTrack = Sequence()
    for target in targets:
        targetToon = target['toon']
        hp = min(targetToon.hp + target['hp'], targetToon.maxHp)
        reactIval = Func(__healToon, targetToon, hp, ineffective)
        if first == 1:
            targetTrack.append(Wait(delay))
            first = 0
        
        targetTrack.append(reactIval)
    
    mtrack = Parallel(Wait(3.0), targetTrack)
    track.append(mtrack)
    track.append(__teleportOut(heal, pet))
    for target in targets:
        targetToon = target['toon']
        track.append(Func(targetToon.clearChat))
    
    return track

