# File: D (Python 2.2)

from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.pets import PetTraits
from toontown.pets import PetMood, PetTricks
from toontown.toonbase import ToontownGlobals
import string

class DistributedPetProxy(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPetProxy')
    
    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self._DistributedPetProxy__funcsToDelete = []
        self._DistributedPetProxy__generateDistTraitFuncs()
        self._DistributedPetProxy__generateDistMoodFuncs()

    
    def generate(self):
        self.traitList = [
            0] * PetTraits.PetTraits.NumTraits
        self.requiredMoodComponents = { }

    
    def getSetterName(self, valueName, prefix = 'set'):
        return '%s%s%s' % (prefix, string.upper(valueName[0]), valueName[1:])

    
    def setPetName(self, petName):
        self.petName = petName

    
    def setTraitSeed(self, traitSeed):
        self.traitSeed = traitSeed

    
    def _DistributedPetProxy__generateDistTraitFuncs(self):
        for i in xrange(PetTraits.PetTraits.NumTraits):
            traitName = PetTraits.getTraitNames()[i]
            setterName = self.getSetterName(traitName)
            
            def traitSetter(value, self = self, i = i):
                self.traitList[i] = value

            self.__dict__[setterName] = traitSetter
            self._DistributedPetProxy__funcsToDelete.append(setterName)
        

    
    def setHead(self, head):
        DistributedPetProxy.notify.setDebug('setHead: %s' % head)
        self.head = head

    
    def setEars(self, ears):
        DistributedPetProxy.notify.setDebug('setEars: %s' % ears)
        self.ears = ears

    
    def setNose(self, nose):
        DistributedPetProxy.notify.setDebug('setNose: %s' % nose)
        self.nose = nose

    
    def setTail(self, tail):
        DistributedPetProxy.notify.setDebug('setTail: %s' % tail)
        self.tail = tail

    
    def setBodyTexture(self, bodyTexture):
        DistributedPetProxy.notify.setDebug('setBodyTexture: %s' % bodyTexture)
        self.bodyTexture = bodyTexture

    
    def setColor(self, color):
        DistributedPetProxy.notify.setDebug('setColor: %s' % color)
        self.color = color

    
    def setColorScale(self, colorScale):
        DistributedPetProxy.notify.setDebug('setColorScale: %s' % colorScale)
        self.colorScale = colorScale

    
    def setEyeColor(self, eyeColor):
        DistributedPetProxy.notify.setDebug('setEyeColor: %s' % eyeColor)
        self.eyeColor = eyeColor

    
    def setGender(self, gender):
        DistributedPetProxy.notify.setDebug('setGender: %s' % gender)
        self.gender = gender

    
    def setLastSeenTimestamp(self, timestamp):
        DistributedPetProxy.notify.setDebug('setLastSeenTimestamp: %s' % timestamp)
        self.lastSeenTimestamp = timestamp

    
    def getTimeSinceLastSeen(self):
        t = self.cr.getServerTimeOfDay() - self.lastSeenTimestamp
        return max(0.0, t)

    
    def updateOfflineMood(self):
        self.mood.driftMood(dt = self.getTimeSinceLastSeen(), curMood = self.lastKnownMood)

    
    def _DistributedPetProxy__handleMoodSet(self, component, value):
        if self.isGenerated():
            self.mood.setComponent(component, value)
        else:
            self.requiredMoodComponents[component] = value

    
    def _DistributedPetProxy__generateDistMoodFuncs(self):
        for compName in PetMood.PetMood.Components:
            setterName = self.getSetterName(compName)
            
            def moodSetter(value, self = self, compName = compName):
                self._DistributedPetProxy__handleMoodSet(compName, value)

            self.__dict__[setterName] = moodSetter
            self._DistributedPetProxy__funcsToDelete.append(setterName)
        

    
    def setMood(self, *componentValues):
        for (value, name) in zip(componentValues, PetMood.PetMood.Components):
            setterName = self.getSetterName(name)
            self.__dict__[setterName](value)
        

    
    def announceGenerate(self):
        self.traits = PetTraits.PetTraits(self.traitSeed, ToontownGlobals.ToontownCentral, traitValueList = self.traitList)
        self.mood = PetMood.PetMood(self)
        for (mood, value) in self.requiredMoodComponents.items():
            self.mood.setComponent(mood, value, announce = 0)
        
        self.requiredMoodComponents = { }
        DistributedPetProxy.notify.debug('time since last seen: %s' % self.getTimeSinceLastSeen())
        print 'ANNOUNCE GENERATE PET!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        self.style = [
            self.head,
            self.ears,
            self.nose,
            self.tail,
            self.bodyTexture,
            self.color,
            self.colorScale,
            self.eyeColor,
            self.gender]

    
    def disable(self):
        if hasattr(self, 'lastKnownMood'):
            self.lastKnownMood.destroy()
            del self.lastKnownMood
        
        self.mood.destroy()
        del self.mood
        del self.traits

    
    def delete(self):
        for funcName in self._DistributedPetProxy__funcsToDelete:
            del self.__dict__[funcName]
        


