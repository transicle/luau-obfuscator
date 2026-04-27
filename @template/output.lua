local F1JIlIfFITtltfjIt1FT = game:GetService("Players")
local jj7IfFTltlTJj1 = F1JIlIfFITtltfjIt1FT.LocalPlayer
local TJITFTtlJj1If7FIjFIlfF = jj7IfFTltlTJj1.Character or jj7IfFTltlTJj1.CharacterAdded:Wait()
local Tljtl17jTtFf1tt = TJITFTtlJj1If7FIjFIlfF:FindFirstChild("Humanoid")
lTTjlj17FIfjlT771J1F7F = 64
local function IIjTffl7l77IJ7lj1Ttt1f(lFjJjFjJlTFl1I7f1TJ)
    local j17FjlltTI1FlJl1FfF = lFjJjFjJlTFl1I7f1TJ:FindFirstChild("Humanoid")
    j17FjlltTI1FlJl1FfF.WalkSpeed = lTTjlj17FIfjlT771J1F7F
end
Tljtl17jTtFf1tt.WalkSpeed = lTTjlj17FIfjlT771J1F7F
jj7IfFTltlTJj1.CharacterAdded:Connect(IIjTffl7l77IJ7lj1Ttt1f)