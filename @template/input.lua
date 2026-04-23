local Players = game:GetService("Players")

local localPlayer = Players.LocalPlayer
local character = localPlayer.Character or localPlayer.CharacterAdded:Wait()
local humanoid = character:FindFirstChild("Humanoid")

desiredSpeed = 64
local function applyWalkspeed(newCharacter)
    local humanoid = newCharacter:FindFirstChild("Humanoid")

    humanoid.WalkSpeed = desiredSpeed
end

humanoid.WalkSpeed = desiredSpeed

localPlayer.CharacterAdded:Connect(applyWalkspeed)