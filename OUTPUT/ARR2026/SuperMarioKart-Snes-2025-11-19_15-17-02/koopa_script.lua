-- Mario Kart RL Reward Script

-- State tracking
current_checkpoint_index = 1
checkpoint_list = {35, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34}
--checkpoint_list = {29, 30, 31, 32, 33, 34, 35}
end_condition = false
passed_checkpoints = {}
data.r = 0
stuck_counter = 0


-- Movement reward to encourage speed-based reward & stuck penalties 
function movementReward()
    local reward = 0

        -- Speed Limit based penalty (global)
    if data.kart1_speed > 775 then
        reward = reward - (data.kart1_speed * 0.005)
    end


    -- Stuck Counter for not moving
    if data.kart1_speed < 1.0 then
        stuck_counter = stuck_counter + 1
        if stuck_counter > 10 then
            reward = reward - 1.0
        end
    else
        stuck_counter = 0 --rest if moving
    end

    -- Not facing the right way
    if data.isTurnedAround == 1 then
        reward = reward - 5
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

-- Road Reward for staying on the sand
function roadReward()
    local reward = 0
    if data.surface == 74 then -- Big bonus for being on sand
        reward = reward 
    elseif (data.surface == 72) and (data.kart1_speed > 700) then -- Small bonus for being on wet sand
        reward = reward - 3 
    --elseif (data.surface == 92) and (data.kart1_speed > 700) then -- Small penalty for being in shallow water
    --    reward = reward - 5
    --elseif data.status == 8 then -- Penalty for being in deep water
    --    reward = reward -- - 10
    --elseif data.surface == 90 then -- Big penalty for being on grass
    --    reward = reward -- - 0.5
    end


    return reward
end

-- Time reward to finish faster, scaled with taking longer.
function timeReward()
    local reward = 0
    local startFrame = 350 -- Note: The frame count for this scenario starts at #280. This needs to be adjusted per scenario
    local scale = 0.0001
    local max_penalty = -3 -- Don't let the penalty dominate

    reward = math.max(-(data.getFrame - startFrame)*scale, max_penalty) -- This gives a small penalty every timeframe.
    return reward
end

-- Reward to incentivize hitting a fish. This is important for our collision recovery tests
function collisionReward()
    local reward = 0

    if data.collision_detection ~= 0 then
        reward = 500
    end

    return reward
end

-- Penalty to prevent deep water swimming
function statusReward()
    local reward = 0

    if data.status ~= 0 then
        reward = -50
    end

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

        -- 5. Collision Reward (sparse)
        total_reward = total_reward + collisionReward()

        -- 6. Status Reward to prevent deep water swimming (sparse)
        total_reward = total_reward + statusReward()
        
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
    if (data.currSec > 35) and (data.currSec < 150) then -- prevents the weird bogus 5555 I'm getting
        --print('Timed out at checkpoint:' .. data.current_checkpoint .. " with reward:" .. data.r)
        return true
    end
    if end_condition == true then
        print('Successfully reached the goal. Training reward: ' .. data.r)
    end
    return end_condition
end
