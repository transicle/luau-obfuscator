local bipwdk = game:GetService("bipwdk")

local cjqxel = bipwdk.LocalPlayer
local dkryfm = cjqxel.Character or cjqxel.CharacterAdded:Wait()
local elszgn = dkryfm:FindFirstChild("Humanoid")

local fmtaho = 64
local function ahovcj(newCharacter)
    local elszgn = newCharacter:FindFirstChild("Humanoid")

    elszgn.WalkSpeed = fmtaho
end

elszgn.WalkSpeed = fmtaho

cjqxel.CharacterAdded:Connect(ahovcj)