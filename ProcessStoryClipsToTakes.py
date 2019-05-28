from pyfbsdk import*

# Process all clips in Character Story Track to Separate Takes
# Sets clip to Zero start time
# Plot animation to character
# Uses clip name as Take Name
# Adds "processedClipTag" to clip name

processedClipTag = "_Processed_Story_Clip"

def plot_clip_options():
    """
    Set Plot Options
    """
    plotClipOptions = FBPlotOptions()
    plotClipOptions.ConstantKeyReducerKeepOneKey = False
    plotClipOptions.PlotAllTakes = False
    plotClipOptions.PlotOnFrame = True
    plotClipOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
    plotClipOptions.PlotTranslationOnRootOnly = False
    plotClipOptions.PreciseTimeDiscontinuities = False
    plotClipOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
    plotClipOptions.UseConstantKeyReducer = False
    
    return plotClipOptions

def create_temp_character_track(character_asset):
    """
    Insert Temp Character Animation Track
    """
    characterTrack = FBStoryTrack(FBStoryTrackType.kFBStoryTrackCharacter, FBStory().RootFolder)
    # Append character to the track
    characterTrack.Details.append (character_asset)
    # Rename track using characterName
    characterTrack.Name = "TEMP"
    
    return characterTrack

for track in FBStory().RootFolder.Tracks:
    # Check Track Type is Character Animation Track
    if track.Type is FBStoryTrackType.kFBStoryTrackCharacter:
        # Get Character in Track
        trackCharacter = track.Character
        # Create Empty List for FBStoryClips
        clonedStoryClipList = []
        for storyClip in track.Clips:
            # Clone the Clip
            cloneClip = storyClip.Clone()
            # Rename Clone Clip
            cloneClip.Name = storyClip.Name + processedClipTag
            # Add Clip to Clip List
            clonedStoryClipList.append(cloneClip)
        for cloneStoryClip in clonedStoryClipList:
            # Create Temp Story Track to Process Clips
            tempTrack = create_temp_character_track(trackCharacter) 
            # Add Clone Clip to Temp Story Track
            tempTrack.Clips.append(cloneStoryClip)
            # Move Clip to Frame Zero (True = Force clip to find the nearest position if the move fail.)
            cloneStoryClip.MoveTo( FBTime(0,0,0,0), True )
            # Get Start Stop of Clone Clip as FBTime()
            cloneClipStartTime = cloneStoryClip.Start
            cloneClipStopTime = cloneStoryClip.Stop
            # Create Take with Clip Name
            newTake = FBTake(cloneStoryClip.Name)
            # Add New Take to Scene
            FBSystem().Scene.Takes.append(newTake)
            # Switch to New Take
            FBSystem().CurrentTake = FBSystem().Scene.Takes[-1]
            # Frame Clone Clip in Take
            FBSystem().CurrentTake.LocalTimeSpan = FBTimeSpan(cloneClipStartTime, cloneClipStopTime)        
            # Mute Original Story Track
            track.Mute = True
            # Get Character in Temp Track
            tempCharacter = tempTrack.Character
            # Select Objects in Temp Character 
            tempCharacter.SelectModels(True, True, False, False)
            # Plot Selected in Current Take
            FBSystem().CurrentTake.PlotTakeOnSelected( plot_clip_options() )
            # Delete Temp Track
            tempTrack.FBDelete()

