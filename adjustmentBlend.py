from pyfbsdk import *
                            
def getBaseLayerPerFrameValueChange(scene_object ):
    """
    Switch to BaseAnimation Layer
    Create Dictionary for per Keyframe Difference Vaule
    Process 'Lcl Translation' + 'Lcl Rotation' Anim Nodes
    Calcuate Difference Value For Every Keyframe on Every Axis FCurve
    Return Dictionary  
    """
    listOfAnimNodesNamesToCheck = ['Lcl Translation', 'Lcl Rotation']
    # Switch to Base Layer
    FBSystem().CurrentTake.SetCurrentLayer(0)
    # Create Empty Dictionary for Values
    transformNodeName_transformAxisName_FcurveKeyFrame_diffValue = {}
    # Iterate over Nodes in Animation Nodes
    for transformNode in scene_object.AnimationNode.Nodes:
        # Only Check Nodes in listOfAnimNodesNamesToCheck
        if not transformNode.Name in listOfAnimNodesNamesToCheck:
            print "CHANGE VALUE WARNING:\n - '{}' Not In List Of Anim Nodes To Check. Ignoring....".format(transformNode.Name)
            continue
        # Check for Key Frames
        if not transformNode.KeyCount > 0:
            print "CHANGE VALUE WARNING:\n - '{}' Has No Key Frames on '{}' Layer. Ignoring....".format(transformNode.Name, FBSystem().CurrentTake.GetLayer(0).Name)
            continue
        # Set Animation Node Node Name as Key in Dictionary
        transformNodeName_transformAxisName_FcurveKeyFrame_diffValue[transformNode.Name] = {}
        # Iterate over axes in Transform Animation Node
        for transformAxis in transformNode.Nodes:
            # Add Transforma Axis Name to dict
            transformNodeName_transformAxisName_FcurveKeyFrame_diffValue[transformNode.Name][transformAxis.Name] = {}
            # Check FCurve has Key Frames
            if not transformAxis.KeyCount > 0:
                print "CHANGE VALUE WARNING:\n - '{}' Has No Key Frames on '{}' Layer. Ignoring....".format(transformNode.Name + " " + transformAxis.Name, FBSystem().CurrentTake.GetLayer(0).Name)
                continue
            # Get Start Value of Animation
            startValue = transformAxis.FCurve.Evaluate(FBSystem().CurrentTake.LocalTimeSpan.GetStart())
            # Iterate over Keys on FCurve 
            for keyOnFCurve in transformAxis.FCurve.Keys:
                # Calculate difference between current and previous key
                differenceValue = keyOnFCurve.Value - startValue
                # Add data to dictionary
                transformNodeName_transformAxisName_FcurveKeyFrame_diffValue[transformNode.Name][transformAxis.Name][keyOnFCurve.Time.GetFrame()] = abs(differenceValue)
                # Reset Start Values to Current Key Value
                startValue = keyOnFCurve.Value            
            
    return transformNodeName_transformAxisName_FcurveKeyFrame_diffValue

def adjustBlend(scene_object):
    """
    Switch To Layer 1
    Calculate Motion Delta
    Apply Motion Delta to FCurve
    """ 
    transNodeName_transAxisName_keyFrame_differenceValue = getBaseLayerPerFrameValueChange( scene_object )
    # Check Dictionary 
    if not transNodeName_transAxisName_keyFrame_differenceValue:
        print "ADJUST BLEND ERROR: Dictionary EMPTY"
    else:
        # Switch to AnimLayer 1
        FBSystem().CurrentTake.SetCurrentLayer(1)
        for transNode in scene_object.AnimationNode.Nodes:
            # Check for Transformation Node in Dictionary
            if not transNode.Name in transNodeName_transAxisName_keyFrame_differenceValue:
                print "ADJUST BLEND WARNING:\n - '{}' No in Dictionary.\n   - Ignoring....\n".format(transNode.Name)
                continue
            # Check Transformation Node Has Key Frames
            if not transNode.KeyCount > 0:
                print "ADJUST BLEND WARNING:\n - '{}' Has No Key Frames on '{}' Layer.\n   - Ignoring....\n".format(transNode.Name, FBSystem().CurrentTake.GetLayer(1).Name)
                continue
            for transAxis in transNode.Nodes:
                # Check Transformation Axis Has Key Frames
                if not transAxis.KeyCount > 0:
                    print "ADJUST BLEND WARNING:\n - '{}' Has No Key Frames on '{}' Layer.\n   - Ignoring....\n".format(transNode.Name + " " + transAxis.Name, FBSystem().CurrentTake.GetLayer(1).Name)
                    continue
                # Get Start Value
                startValue = transAxis.FCurve.Evaluate(FBSystem().CurrentTake.LocalTimeSpan.GetStart())
                endValue = transAxis.FCurve.Evaluate(FBSystem().CurrentTake.LocalTimeSpan.GetStop())
                if transAxis.Name in transNodeName_transAxisName_keyFrame_differenceValue[transNode.Name]:
                    deltaValue = startValue                  
                    # Get Total Amount of Change
                    totalAmountOfChange = sum(transNodeName_transAxisName_keyFrame_differenceValue[transNode.Name][transAxis.Name].values())
                    for keyFrame in sorted(transNodeName_transAxisName_keyFrame_differenceValue[transNode.Name][transAxis.Name].keys()):
                        valueChange = transNodeName_transAxisName_keyFrame_differenceValue[transNode.Name][transAxis.Name][keyFrame]
                        # Calc Percentage Change
                        # Catch Zero Division Error
                        if valueChange > 0.0:
                            percentChange = ( valueChange / totalAmountOfChange ) * 100.0
                        else:
                            percentChange = 0.0
                        # Calc Increment Change
                        incrementChangeValue = (percentChange * endValue) / 100.0
                        # Calc Delta Value
                        deltaValue = deltaValue + incrementChangeValue
                        # Apply Delta Value to FCurve
                        transAxis.FCurve.KeyAdd( FBTime(0, 0, 0, keyFrame), deltaValue)
                                
def fixFootSlide():
    """
    Check More than 1 Anim Layer
    Get Current Character
    Apply Adjustment Blend to Every Effector Model
    """
    if not FBSystem().CurrentTake.GetLayerCount() > 1:
        print "FIX SLIDE ERROR:\n - Only Single '{}' Layer Found".format(FBSystem().CurrentTake.GetLayer(0).Name)
    else:
        currentChar = FBApplication().CurrentCharacter
        if currentChar:
            for lEffectorId in FBEffectorId.values.values():
                characterEffector = currentChar.GetEffectorModel(lEffectorId)
                if characterEffector:
                    adjustBlend( characterEffector)
        else:
             print "FIX SLIDE ERROR:\n - Current Character Not Found"

fixFootSlide()