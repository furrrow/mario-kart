-- Mario Kart RL Reward Script: Speed + Checkpoint Bonus

-- CONFIGURABLE PARAMETERS
CHECKPOINT_BONUS = 10.0      -- Reward for passing a checkpoint
SPEED_SCALE      = 0.1       -- Scale to convert speed to reward
STUCK_PENALTY = 0.5          -- Pentalty for zero/low speed
STUCK_THRESHOLD = 5          -- Frames with speed < 1.0

-- State tracking
current_checkpoint_index = 1
checkpoint_list = {29, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28}
end_condition = false
passed_checkpoints = {}
data.r = 0
stuck_counter = 0


-- Movement reward to encourage speed-based reward & stuck penalties 
function movementReward()
    local reward = 0

    -- Speed Limit based penalty (global)
    if data.kart1_speed > 900 then
        reward = reward - (data.kart1_speed * 0.025)
    end

    -- Stuck Counter for not moving
    if data.kart1_speed < 1.0 then
        stuck_counter = stuck_counter + 1
        if stuck_counter > 10 then
            reward = reward - 0.5
        end
    else
        stuck_counter = 0 --rest if moving
    end

    if data.isTurnedAround == 1 then
        reward = reward - 5.0
    end

    return reward
end

-- Checkpoint Reward for passing checkpoints along the path
function checkpointReward()
    local reward = 0
    local expected_next = checkpoint_list[current_checkpoint_index + 1]
    local progress_fraction = current_checkpoint_index / (#checkpoint_list)

    -- Check if data is valid
    if type(data) ~= "table" or data.current_checkpoint == nil then
        print("[Lua] ⚠️ Data not ready. Skipping reward calculation.")
        return 0
    end

    -- Check if the agent has passed the next checkpoint in the list
    if data.current_checkpoint == expected_next and not passed_checkpoints[expected_next] then
        reward = reward + (100*progress_fraction*2)
        passed_checkpoints[expected_next] = true
        current_checkpoint_index = current_checkpoint_index + 1
        --print("[Lua] 🚩 Passed checkpoint " .. data.current_checkpoint .."! Bonus awarded.")

    end

    return reward
end

-- Road Reward for staying on the road
function roadReward()
    local reward = 0
    

    if data.surface ~= 64 then
        reward = reward - 10
        if data.current_checkpoint > 10 then -- Apply a stronger penalty in the second half
            reward = reward - 90
        end
    end

    return reward
end

-- Time reward to finish faster, scaled with taking longer.
function timeReward()
    local reward = 0
    local startFrame = 350 -- Note: The frame count for this scenario starts at #280. This needs to be adjusted per scenario
    local scale = 0.0001
    local max_penalty = -15 -- Don't let the penalty dominate

    reward = math.max(-(data.getFrame - startFrame)*scale, max_penalty) -- This gives a small penalty every timeframe.

    return reward
end



-- Called every step
function getReward()
    -- Check that data is valid
    if type(data) ~= "table" or not data.kart1_speed or not data.current_checkpoint then
        print("[Lua] ⚠️ Data not ready. Skipping reward calculation.")
        return 0
    end

    local total_reward = 0

    --- Removing all penalties applied prior to the start!
    if data.getFrame > 350 then
        -- 1. Speed-based reward (dense)
        total_reward = total_reward + movementReward()
        -- 2. Checkpoint bonus (sparse)
        total_reward = total_reward + checkpointReward()

        -- 3. Road reward (sparse)
        total_reward = total_reward + roadReward()

        -- 4. Time reward/penalty (dense)
        total_reward = total_reward + timeReward()

        -- Add a terminal bonus for finishing the race
        --if data.current_checkpoint == #checkpoint_list then
        if data.lap == 129 then
            total_reward = total_reward + 300
            end_condition = true
        end
    end

    data.r = data.r + total_reward
    return total_reward
end


function isDone()
    if (data.currSec > 37) and (data.currSec < 150) then -- prevents the weird bogus 5555 I'm getting
        print('Timed out at checkpoint:' .. data.current_checkpoint .. " with reward:" .. data.r)
        return true
    end
    if end_condition == true then
        print('Successfully reached the goal. Training reward: ' .. data.r)
    end
    return end_condition
end
