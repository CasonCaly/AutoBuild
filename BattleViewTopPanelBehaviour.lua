--------------------------------------------------------
--- 战斗中的上方面板
-- @copyright(c) ©2016福州博翼互娱网络科技有限公司
-- @author hsl
-- @release 2016/9/14
--------------------------------------------------------
require "Game.Model.UpgradeModel"

unity.exports.BattleViewTopPanelBehaviour = class("BattleViewTopPanelBehaviour", ViewBehaviour)

local UpdateBeat = UpdateBeat

local null = null

local NumTypeEnum = {
   kMoney = "Money",
   kExp = "Exp",
}

function BattleViewTopPanelBehaviour:Ctor()
    self.heroData = DataCenter.Get(HeroData)
    self.battleData = DataCenter.Instance().BattleData.Data
    self.checkpointStatic = StaticPool.Get(CheckpointStatic)
    self.currencyCheckPoint = StaticPool.Get(CurrencyCheckpointStatic)
    self.childCheckPoint = StaticPool.Get(ChildCheckpointStatic)
    self.playLevelStatic = StaticPool.Get(PlayLevelStatic)
    self.mysteriousnessData = DataCenter.Get(MysteriousData)
    self.level = self.heroData:Level()
    self.gold = self.heroData:Gold()
    self.diamond = self.heroData:Diamond()
    self.exp = self.heroData:Exp()
    self.curExp = self.heroData:CurExp()
    self.animationExp = 0
    self.animationGold = 0
    self.deltaExp = self.exp
    self.deltaGold = self.gold
    self.condition = 0
    self.coinAcctime = 0.0
    self.gemAcctime = 0.0
    self.tweenerCoinNum = 0
    self.tweenerGemNum = 0
    self.tweenerCoin = null
    self.tweenerGem = null
    self.bossAcctime = 0.0
    self.mysteriousnessLogic = MysteriousnessLogic.new(self)
    self.accGold = 0
    self.accExp = 0
    self.goldCDtween = nil
    self.goldAudioCDtween = nil
    self.expCDtween = nil
    self.rewardGoldEmitterCount = 0
    self.rewardExpEmitterCount = 0
    self.accRewardItem = Map.new()
    
    self.goldList = List.new()
    self.expList = List.new()
    
    self.addGoldPrefab = Util.LoadPrefab("UI/Battle/AddGold")

    self.leftFloorList = Map.new()
    self.middleFloorList = Map.new()
    self.rightFloorList = Map.new()

    ViewBehaviour.Ctor(self)
    UpdateBeat:Add(self.Update, self)
    self:InitUI()

    EventCenter.Add(BattleEvtEnum.kInitRoltFinish, self, self.OnRoleInitFinish)
    EventCenter.Add(RoleInfoMsgEnum.kUpdateDiamond, self, self.OnUpdateDiamond)

    EventCenter.Add("LuaDestroy",self,self.OnMainDestroy)
    EventCenter.Add(EquipMsg.kLevelUp, self, self.OnEquipLevelUpEvent)
end 

function BattleViewTopPanelBehaviour:Reset()
    self.rewardGoldEmitterCount = 0
    self.rewardExpEmitterCount = 0
    self.accGold = 0
    self.accExp = 0
    self.accRewardItem:Clear()
    self.condition = 0
    self.coinAcctime = 0.0
    self.gemAcctime = 0.0
    self.tweenerCoinNum = 0
    self.tweenerGemNum = 0
    self.tweenerCoin = null
    self.tweenerGem = null
    self.bossAcctime = 0.0
    self:Init()
end

function BattleViewTopPanelBehaviour:OnMainDestroy()

end

function BattleViewTopPanelBehaviour:OnUpdateDiamond()
    local justice = DataCenter.Get(HeroData):GetHero()
    self.gemtext.text = self:ChangeNumberToKBMT(self.heroData:Diamond())
end

function BattleViewTopPanelBehaviour:OnRoleInitFinish()
    self.accGold = 0
    self.accExp = 0
    self.accRewardItem:Clear()
    self.coinImage = self.coinAttr.transform:Find("image")
    self.lvImage = self.floorProgress.transform:FindChild("image")
    local justice = DataCenter.Get(HeroData):GetHero()
    local heroData = DataCenter.Get(HeroData)
    local mysteriousData = DataCenter.Get(MysteriousData)
    self.level = heroData:Level()
    self.gold = heroData:Gold()
    self.diamond = heroData:Diamond()
    self.exp = heroData:Exp()
    self.curExp = heroData:CurExp()
    self.deltaExp = self.exp
    self.deltaGold = self.gold

    -- 初始化装备
    local equipData = DataCenter.Get(EquipData)
    equipData:Init(heroData:Id())
    local equipedMap = equipData:EquipedMap()
    for k, equipItem in equipedMap:pairs() do
        EquipModel.CommitPropertyToPlayer(nil, equipItem)
    end

    -- 初始化任务
    local taskData = DataCenter.Get(TaskData)
    taskData:Init(heroData:Id())
    taskData:IsResetTaskList()

    -- 初始化任务
    local thingData = DataCenter.Get(ThingData)
    thingData:Init(heroData:Id())

    if mysteriousData:IsMysteriousness() then
        self.fightBtn.interactable = false
        self.mysteriousnessLogic:Init(self.mysteriousnessData:CurrGateId())
    else
        self.fightBtn.interactable = true
        self.time.gameObject:SetActive(false)
        local killMonster = self.battleData.curKillingCount
        local item = self.centerFloorStatic
        self.condition = item:Condition() - killMonster
        self.taskTxt.text = string.format(L("killMonster"),self.condition)
        self.taskProgressFront.fillAmount = killMonster / item:Condition()
    end

    local level = self.heroData:Level()

    if level > 1 then
        UpgradeModel.UpdateLevel(level - 1, level,false)
    end

    --local nextlvItem = self.playLevelStatic:GetByKey(level + 1)
    --if nextlvItem then 
    --    self.progressFront.fillAmount = self.curExp / nextlvItem:Exp()
    --end

    self:InitUI()
end

function BattleViewTopPanelBehaviour:OnSpawnBoss()
    local boss = DataCenter.Instance().BattleData.CurrBoss
    if boss ~= nil then
        boss:AddHPDelegate(function (curr,max)
            local tweener = DG.Tweening.DOTween.To(handler(self,
		        function ()
			        return self.bossProgressFront.fillAmount
		        end),
		        handler(self,function ()
                    return
		        end),
		        curr/max,
		        0.2)
            tweener:SetAutoKill(true)
	        tweener:SetEase(DG.Tweening.Ease.OutExpo)
            tweener:OnStart(
		        handler(self,function ()
                    self.bossAcctime = 0.0
		        end))
	        tweener:OnComplete(
		        handler(self,function ()
			        self.bossAcctime = 0.0
		        end))
	        tweener:OnUpdate(
		        handler(self,function ()
			        self.bossAcctime = self.bossAcctime + UnityEngine.Time.deltaTime
                    local value = self.bossProgressFront.fillAmount
                    local num = value - (value - curr/max)*(self.bossAcctime/0.2)
			        self.bossProgressFront.fillAmount = num
		        end))
        end)
    end
end

function BattleViewTopPanelBehaviour:PlayAddGold(obj,pos,money)
    local uiCanvas = GameObject.Find("2dUICanvas");
    local canvasRectTrans = uiCanvas.transform:GetComponent("RectTransform");
    local parent = GameObject.FindGameObjectWithTag("UIRoot");
	local objInstance = newObject(self.addGoldPrefab)
	local text = objInstance.transform:GetComponent('Text')
	text.transform:SetParent(uiCanvas.transform,false)
	text.transform.localPosition = Vector3.New(0.0,0.0,0.0)
	--text.transform.localScale = Vector3.New(1.0,1.0,1.0)
    text.text = "+"..money
    local mainCam = Singleton_CameraGroup.Instance.followCamera
    local uiCam = Singleton_CameraGroup.Instance.uiCamera

    local screenPos = UnityEngine.RectTransformUtility.WorldToScreenPoint(mainCam, pos)
    local uipos = Vector2.New(100.0,100.0)
    local success, uipos = UnityEngine.RectTransformUtility.ScreenPointToLocalPointInRectangle(canvasRectTrans, screenPos, uiCam, uipos)
    local rectTrans = text.transform:GetComponent("RectTransform");
    rectTrans.localPosition = Vector3.New(uipos.x,uipos.y,0.0)

    local tweener = text.transform:GetComponent('DOTweenAnimation')
	tweener.hasOnComplete = true
	local tween = tweener.tween
	tween:OnComplete(handler(self,function ()
			text.transform:SetParent(nil, false)
			GameObject.Destroy (text.gameObject)
		end))
end

function BattleViewTopPanelBehaviour:InitUI()
    self.lvltext.text = string.format("%d", self.heroData:Level())
    self.cointext.text = self:ChangeNumberToKBMT(self.heroData:Gold())
    self.gemtext.text = self:ChangeNumberToKBMT(self.heroData:Diamond())
    self:UpdateLevelUI()
end

function BattleViewTopPanelBehaviour:Update()
    if self.tweenerCoinNum > 0 then
        self.tweenerCoinNum = self.tweenerCoinNum - 1
        self:PlayCoinAnimation()
    end
    if self.tweenerGemNum > 0 then
        self.tweenerGemNum = self.tweenerGemNum - 1
        self:PlayGemAnimation()
    end
    if nil ~= self.mysteriousnessLogic then
        self.mysteriousnessLogic:Update()
    end
end

function BattleViewTopPanelBehaviour:PlayCoinAnimation()
    if self.goldList:Size() <= 0 then
        return
    end
    if self.tweenerCoin ~= null and self.tweenerCoin:IsPlaying() then
        logWarn("tweenerCoin:IsPlaying")
        self.animationGold = self.goldList:PopFront();
		return
	end
    self.animationGold = self.goldList:PopFront();
    self.tweenerCoin = DG.Tweening.DOTween.To(handler(self,
		function ()
			return self.gold
		end),
		handler(self,function ()
			self:SetValue(self.cointext, self.deltaGold, NumTypeEnum.kMoney)
		end),
		self.animationGold,
		1.0)
    self.tweenerCoin:SetAutoKill(true)
	self.tweenerCoin:SetEase(DG.Tweening.Ease.Linear)
    self.tweenerCoin:OnStart(
		handler(self,function ()
            self.coinAcctime = 0.0
		end
		))
	self.tweenerCoin:OnComplete(
		handler(self,function ()
			self:SetValue(self.cointext,self.animationGold, NumTypeEnum.kMoney)
		end
		))
	self.tweenerCoin:OnUpdate(
		handler(self,function ()
			self.coinAcctime = self.coinAcctime + UnityEngine.Time.deltaTime
            local num = (self.animationGold - self.deltaGold)*(self.coinAcctime/1.0)+self.deltaGold
			self.cointext.text = self:ChangeNumberToKBMT(num)
		end
		))
end

function BattleViewTopPanelBehaviour:PlayGemAnimation()
    if self.expList:Size() <= 0 then
        return
    end
    if self.tweenerGem ~= null and self.tweenerGem:IsPlaying() then
        self.animationExp = self.expList:PopFront();
		return
	end
    self.animationExp = self.expList:PopFront();
    self.tweenerGem = DG.Tweening.DOTween.To(handler(self,
		function ()
			return self.exp
		end),
		handler(self,function ()
			self:SetValue(self.gemtext, self.deltaExp, NumTypeEnum.kExp)
		end),
		self.animationExp,
		1.0)
    self.tweenerGem:SetAutoKill(true)
	self.tweenerGem:SetEase(DG.Tweening.Ease.Linear)
    self.tweenerGem:OnStart(
		handler(self,function ()
            self.gemAcctime = 0.0
		end
		))
	self.tweenerGem:OnComplete(
		handler(self,function ()
			self:SetValue(self.gemtext,self.animationExp, NumTypeEnum.kExp)
		end
		))
	self.tweenerGem:OnUpdate(
		handler(self,function ()
			self.gemAcctime = self.gemAcctime + UnityEngine.Time.deltaTime
            local num = (self.animationExp - self.deltaExp)*(self.gemAcctime/1.0)+self.deltaExp
			self.gemtext.text = self:ChangeNumberToKBMT(num)
		end
		))


end

function BattleViewTopPanelBehaviour:ChangeNumberToKBMT(num)
    if num >= 100000000000 then
        return string.format("%.2fT", num / 1000000000)
    elseif num >= 100000000 then
        return string.format("%.2fM", num / 1000000)
    elseif num >= 100000 then
        return string.format("%.2fK", num / 1000)
    else
        return string.format("%d", num)
    end
end

function BattleViewTopPanelBehaviour:OnFriendDeathHandler()
    local item = self.centerFloorStatic
    if self.mysteriousnessData:IsMysteriousness() then
        local currencyItem = self.currencyCheckPoint:GetByKey(self.mysteriousnessData:CurrGateId())
        item = self.childCheckPoint:GetByKey(currencyItem:ChildId())
        self.mysteriousnessLogic:DevilDeathHandler()
    end
end

function BattleViewTopPanelBehaviour:DevilDeathHandler()
    local item = self.centerFloorStatic
    if self.mysteriousnessData:IsMysteriousness() then
        local currencyItem = self.currencyCheckPoint:GetByKey(self.mysteriousnessData:CurrGateId())
        item = self.childCheckPoint:GetByKey(currencyItem:ChildId())
        self.mysteriousnessLogic:DevilDeathHandler()
    else
        self.condition = self.condition - 1
        self.taskTxt.text = string.format(L("killMonster"),self.condition)
        self.taskProgressFront.fillAmount = (item:Condition() - self.condition) / item:Condition()
        self.battleData.curKillingCount = item:Condition() - self.condition
    end

    local battleData = DataCenter.Instance().BattleData
    local deathEvailRole = battleData.DeathEvailRole

    self.normalGold = math.random(tonumber(item:GetGold(1)),tonumber(item:GetGold(2)))
    self.normalExp = item:PlayerExp()
    self.bossGold = math.random(tonumber(item:GetBossGold(1)),tonumber(item:GetBossGold(2)))
    self.bossExp = item:BossPlayerExp()
    if deathEvailRole.roleType == CommonEnum.EnumRoleType.kBoss then
        self.accGold = self.accGold + self.bossGold
        self.accExp = self.accExp + self.bossExp
        self.gold = self.gold + self.bossGold
        self.exp = self.exp + self.bossExp
        self.curExp = self.curExp + self.bossExp
        DataCenter.Get(PetData):AddFightExp(self.bossExp)
        if self.bossGold > 0 then
            self:PlayAddGold(self.bossGold,deathEvailRole.transform.position,self.bossGold)
        end
    else
        self.accGold = self.accGold + self.normalGold
        self.accExp = self.accExp + self.normalExp
        self.gold = self.gold + self.normalGold
        self.exp = self.exp + self.normalExp
        self.curExp = self.curExp + self.normalExp
        DataCenter.Get(PetData):AddFightExp(self.normalExp)
        if self.normalGold > 0 then
            self:PlayAddGold(self.normalGold,deathEvailRole.transform.position,self.normalGold)
        end
    end

    self.level,self.curExp = UpgradeModel.ComputerExp(self.level,self.curExp)

    self.goldList:PushBack(self.gold)
    self.expList:PushBack(self.exp)
    
    self.heroData:SetLevel(self.level)
    self.heroData:SetExp(self.exp)
    self.heroData:SetGold(self.gold)
    self.heroData:SetCurExp(self.curExp)
end

function BattleViewTopPanelBehaviour:BossDeathHandler()
    local battleData = DataCenter.Instance().BattleData
    local deathEvailRole = battleData.DeathEvailRole
    local pos = deathEvailRole.transform.position

    local item = self.centerFloorStatic
    self.normalGold = math.random(tonumber(item:GetBossGold(1)),tonumber(item:GetBossGold(2)))
    self.normalPlayerExp = item:BossPlayerExp()
    self.normalPetExp = item:BossPetExp()
    self.gold = self.gold + self.normalGold
    self.exp = self.exp + self.normalPlayerExp
    self.accGold = self.accGold + self.normalGold
    self.accExp = self.accExp + self.normalPlayerExp
    self.curExp = self.curExp + self.normalPlayerExp
    self:PlayAddGold(self.normalGold,deathEvailRole.transform.position,self.normalGold)

    DataCenter.Get(PetData):AddFightExp(self.normalPlayerExp)

    self.level,self.curExp = UpgradeModel.ComputerExp(self.level,self.curExp)

    self.goldList:PushBack(self.gold)
    self.expList:PushBack(self.exp)
    
    self.heroData:SetLevel(self.level)
    self.heroData:SetExp(self.exp)
    self.heroData:SetGold(self.gold)
    self.heroData:SetCurExp(self.curExp)

    
    Util.TimerInLua(0.2,function()
        self:DoFlyRewardsAni(pos)
    end)
    Util.TimerInLua(0.6,function()
        self:DoFlyRewardsAni(pos)
    end)
    Util.TimerInLua(1.0,function()
        self:DoFlyRewardsAni(pos)
    end)

    Util.TimerInLua(1.5,function()
        local rewardView = BattleRewardViewBehaviour.new()
        local item = StaticPool.Get(CheckpointStatic):GetByKey (battleData.CheckPointId)
        local rewardItemList = RewardModel.RandomRewardItem(item,DropOwnterType.kBoss)
        rewardView:FillRewardsList(rewardItemList)
        rewardView:ShowToTop()
    end)
end

function BattleViewTopPanelBehaviour:DestructDeathHandler()
    local item = self.centerFloorStatic
    local lvCnt = self.playLevelStatic:Count()

    local battleData = DataCenter.Instance().BattleData
    local deathEvailRole = battleData.DeathEvailRole
    self.normalGold = math.random(tonumber(item:GetThingsGold(1)),tonumber(item:GetThingsGold(2)))
    self.normalExp = item:ThingsPlayerExp()

    self.gold = self.gold + self.normalGold
    self.exp = self.exp + self.normalExp
    self.accGold = self.accGold + self.normalGold
    self.accExp = self.accExp + self.normalExp
    self.curExp = self.curExp + self.normalExp
    self:PlayAddGold(self.normalGold,deathEvailRole.transform.position,self.normalGold)

    DataCenter.Get(PetData):AddFightExp(self.normalExp)

    self.level,self.curExp = UpgradeModel.ComputerExp(self.level,self.curExp)

    self.goldList:PushBack(self.gold)
    self.expList:PushBack(self.exp)
    
    self.heroData:SetLevel(self.level)
    self.heroData:SetExp(self.exp)
    self.heroData:SetGold(self.gold)
    self.heroData:SetCurExp(self.curExp)
end

function BattleViewTopPanelBehaviour:OnBossUIEvent()
    self.taskProgress.gameObject:SetActive(false)
    self.bossBtn.gameObject:SetActive(true)
end

function BattleViewTopPanelBehaviour:OnNewFloorUIEvent(isMysterious)
    self.accGold = 0
    self.accExp = 0
    self.accRewardItem:Clear()
    local battleData = DataCenter.Instance().BattleData
    self.bossProgress.gameObject:SetActive(false)
    self.taskProgress.gameObject:SetActive(true)
    self.bossBtn.gameObject:SetActive(false)
    local index = battleData.CurFloorIndex;
    local leftFloorStatic = self.checkpointStatic:GetByKey(index - 1)
    local leftFloorType = nil
    if (leftFloorStatic ~= nil) then
        leftFloorType = leftFloorStatic:Type()
    end
    self:ShowFloorType(self.leftFloorList,leftFloorType,index-1)
    
    self.centerFloorStatic = self.checkpointStatic:GetByKey(index)
    local centerFloorType = nil
    if (self.centerFloorStatic ~= nil) then
        centerFloorType = self.centerFloorStatic:Type()
    end
    self:ShowFloorType(self.middleFloorList,centerFloorType,index)

    local rightFloorStatic = self.checkpointStatic:GetByKey(index+1)
    local rightFloorType = nil
    if (rightFloorStatic ~= nil) then
        rightFloorType = rightFloorStatic:Type()
    end
    self:ShowFloorType(self.rightFloorList,rightFloorType,index+1)

    local item = self.centerFloorStatic
    self.taskTxt.text = string.format(L("killMonster"),item:Condition())
    self.condition = item:Condition()
    self.taskProgressFront.fillAmount = 0.0

    self.battleData.curFloorIndex = index
    self:ShowCheckpointTipPanel()
end

function BattleViewTopPanelBehaviour:ShowFloorType(floorList,floorType,index)
    if (floorType == nil) then
        floorList:Find("Num").gameObject:SetActive(false)
        floorList:Find("Img").gameObject:SetActive(true)
        floorList:Find("Boss").gameObject:SetActive(false)
    elseif (floorType == 1) then
        floorList:Find("Num").gameObject:SetActive(true)
        floorList:Find("Num").text = index
        floorList:Find("Img").gameObject:SetActive(false)
        floorList:Find("Boss").gameObject:SetActive(false)
    elseif (floorType == 2) then
        floorList:Find("Num").gameObject:SetActive(false)
        floorList:Find("Img").gameObject:SetActive(false)
        floorList:Find("Boss").gameObject:SetActive(true)
    end
end


function BattleViewTopPanelBehaviour:SetValue(text, val, typeVal)
	text.text = self:ChangeNumberToKBMT(val)
    if typeVal == NumTypeEnum.kMoney then
        self.deltaGold = val
    elseif typeVal == NumTypeEnum.kExp then
        self.deltaExp = val
    end
end


function BattleViewTopPanelBehaviour:OnEquipLevelUpEvent(equipEvent)
    local cost = equipEvent:LevelUpCost()
    local finalGold = self.gold - cost
    self:SetValue(self.cointext,  finalGold)
end

function BattleViewTopPanelBehaviour:GetValue(text)
	return tonumber(text.text)
end

function BattleViewTopPanelBehaviour:OnSkillBtnClick(go)
    local view = SkillViewBehaviour.new()
    view:ShowToTop()
end

function BattleViewTopPanelBehaviour:OnFightBtnClick()
    local view = ChallengeViewBehaviour.new()
    view:ShowToTop()
end

function BattleViewTopPanelBehaviour:OnBossBtnClick()
    Singleton_Entrance.Instance.xpMgr:StopXP()
    local  justiceList =    Singleton_RoleGenerator.Instance.JusticeList 
    for i = 0,justiceList.Count- 1 do 
        justiceList[i]:ChangeState(EnumRoleState.WaitBoss)
    end 
    self.bossBtn.gameObject:SetActive(false)
    Singleton_RoleGenerator.Instance:SetEntityState(CommonEnum.EnumRoleType.kMonster,EnumRoleState.WaitBoss)
    local sequence = DG.Tweening.DOTween.Sequence()
    sequence:Append(EnvironmentCenter.Instance():ChangeEnvironmentAnimation())
    sequence:AppendCallback(function()
              self:ShowBossTipPanel()
        end)
    self.bossProgress.gameObject:SetActive(true)
    self.bossProgressFront.fillAmount = 1.0
end

function BattleViewTopPanelBehaviour:OnXPStart()
    local getXpTip = function()
        return "超爽"  --没有用L
    end

    local getXp = function ()
        -- body
        return "时刻"
    end

    self.bossTipPanel.sprite = Util.LoadSprite ("UI/Main/bossname_bg")
    self:ShowTipPanel(getXpTip, getXp, true)
end

function BattleViewTopPanelBehaviour:ShowBossTipPanel()
    local getBossTip = function()
        return L("boss")
    end

    local getBossName =  function()
        local wc = Singleton_Entrance.Instance:GetWaveController()
        local bossId = wc:StartSpawnBoss()
        local bossMonsterItem = StaticPool.Get(MonsterEditStatic):GetByKey(bossId)
        if nil ~= bossMonsterItem then
            return bossMonsterItem:Name(),bossMonsterItem:Description()
        else
            return nil   
        end    
    end

    self.bossTipPanel.sprite = Util.LoadSprite ("UI/Main/bossname_bg")
    self:ShowTipPanel(getBossTip, getBossName, true)
end

function BattleViewTopPanelBehaviour:ShowCheckpointTipPanel()
    local battleData = DataCenter.Instance().BattleData
    local getNewFloorTip = function()
        return string.formatEx(L("curFloor"), battleData.CurFloorIndex) --tostring(battleData.CurFloorIndex)
    end

    local getNewFloorName =  function()
        local checkpointItem = self.checkpointStatic:GetByKey(battleData.CurFloorIndex)
        if nil == checkpointItem then
            return nil
        else
            return checkpointItem:Name()
        end
    end

    self.bossTipPanel.sprite = Util.LoadSprite ("UI/Main/checkpointname_bg")
    self:ShowTipPanel(getNewFloorTip, getNewFloorName, false)
end

------
-- 显示boss提示面板,面板分为两部分，一个是提示，当是boss时候直接显示boss，是楼层的时候显示第几层。第二部分为boss名字或者楼层名称
-- @param[type=string function()] 一个回调函数，函数需要返回一个字符串
-- @param[type=string function()] 一个回调函数，函数需要返回一个字符串
function BattleViewTopPanelBehaviour:ShowTipPanel(getTipCallback, getNameCallback, isBoss)
    self.bossTipPanel.gameObject:SetActive(true)
    local bossTipPanelTf = self.bossTipPanel.transform;
    local tipTxt = bossTipPanelTf:FindChild("tipTxt"):GetComponent(typeof(UnityEngine.UI.Text))
    local nameTxt = bossTipPanelTf:FindChild("nameTxt"):GetComponent(typeof(UnityEngine.UI.Text))

    tipTxt.gameObject:SetActive(false)
    nameTxt.gameObject:SetActive(false)

    local rf = self.bossTipPanel:GetComponent(typeof(UnityEngine.RectTransform))
    rf.localScale = Vector3(1, 0, 1)
    local doScaleY = rf:DOScaleY(1.0, 0.3)
    local sequence = DG.Tweening.DOTween.Sequence()
    sequence:SetUpdate(true)
    sequence:Append(doScaleY)

    local maxScale = 10
    -- boss 提示文字动画提示
    local tipTxtScaleCb = function()    
        -- 从回调用中获取名字
        local name,desc = getNameCallback()
        if nil ~= name then
            nameTxt.text = name 
            self.bossNameTxt.text = name
            self.bossSkillTxt.text = desc
        end
        nameTxt.gameObject:SetActive(true)
        local nameTxtRf = nameTxt:GetComponent(typeof(UnityEngine.RectTransform))
        nameTxtRf.localScale = Vector3(maxScale, maxScale, maxScale)
        local nameTxtScale = nameTxtRf:DOScale(Vector3(1, 1, 1), 0.25)
        nameTxtScale:SetEase(DG.Tweening.Ease.InCubic)

        local nameSeq = DG.Tweening.DOTween.Sequence()
        nameSeq:SetUpdate(true)
        nameSeq:Append(nameTxtScale)
        nameSeq:AppendInterval(3)
        nameSeq:AppendCallback(function()
          self.bossTipPanel.gameObject:SetActive(false)
          if isBoss then
            local  justiceList =    Singleton_RoleGenerator.Instance.JusticeList 
            for i = 0,justiceList.Count- 1 do 
                justiceList[i]:ChangeState(EnumRoleState.Idle)
            end 
          end
        end)
    end

    -- boss面板的缩放回调
    local panelScaleCb = function()
        -- boss提示文字动画
        tipTxt.gameObject:SetActive(true)
        --  从回调用中获取提示
        local tip = getTipCallback()
        if nil ~= tip then
            tipTxt.text = tip
        end

        local tipTxtRf = tipTxt:GetComponent(typeof(UnityEngine.RectTransform))
        tipTxtRf.localScale = Vector3(maxScale, maxScale, maxScale)
        local tipTxtScale = tipTxtRf:DOScale(Vector3(1, 1, 1), 0.25)

        local tipSeq = DG.Tweening.DOTween.Sequence()
        tipSeq:SetUpdate(true)
        tipSeq:Append(tipTxtScale)
        tipSeq:AppendCallback(tipTxtScaleCb)    
    end
    sequence:AppendCallback(function()
        if isBoss then
            local mainCam = Singleton_CameraGroup.Instance.followCamera
            local tweener = mainCam.transform:GetComponent('DOTweenAnimation')
            tweener:CreateTween()
            tweener:DOPlay()
        end
    end)
    sequence:AppendCallback(panelScaleCb)
end

function BattleViewTopPanelBehaviour:OnDestroy()
    EventCenter.Detach(self)
end

function BattleViewTopPanelBehaviour:Awake()
    self.lvltext.text = "0"
    self.cointext.text = "0"
    self.gemtext.text = "0"
    self.taskProgressFront.fillAmount = 0.0

    local leftNum = self.leftFloor.transform:FindChild("text")
    local leftImg = self.leftFloor.transform:FindChild("img")
    local leftBoss = self.leftFloor.transform:FindChild("boss")
    self.leftFloorList:Insert("Num",leftNum:GetComponent("Text"))
    self.leftFloorList:Insert("Img",leftImg:GetComponent("Image"))
    self.leftFloorList:Insert("Boss",leftBoss:GetComponent("Image"))

    local middleNum = self.middleFloor.transform:FindChild("text")
    local middleImg = self.middleFloor.transform:FindChild("img")
    local middleBoss = self.middleFloor.transform:FindChild("boss")
    self.middleFloorList:Insert("Num",middleNum:GetComponent("Text"))
    self.middleFloorList:Insert("Img",middleImg:GetComponent("Image"))
    self.middleFloorList:Insert("Boss",middleBoss:GetComponent("Image"))

    local rightNum = self.rightFloor.transform:FindChild("text")
    local rightImg = self.rightFloor.transform:FindChild("img")
    local rightBoss = self.rightFloor.transform:FindChild("boss")
    self.rightFloorList:Insert("Num",rightNum:GetComponent("Text"))
    self.rightFloorList:Insert("Img",rightImg:GetComponent("Image"))
    self.rightFloorList:Insert("Boss",rightBoss:GetComponent("Image"))

    self.equipBtn.onClick:AddListener(handler(self, self.OnSkillBtnClick))
    self.bossBtn.onClick:AddListener(handler(self, self.OnBossBtnClick))
    self.fightBtn.onClick:AddListener(handler(self, self.OnFightBtnClick))
    self.exit.onClick:AddListener(handler(self, self.OnExitClick))

    self.chatBtn.onClick:AddListener(handler(self, self.OnChatClickEvent))
    --self.bossBtn.gameObject:SetActive(true)
    EventCenter.Add(BattleEvtEnum.kEvilDeath, self, self.DevilDeathHandler)
    EventCenter.Add(BattleEvtEnum.kDestructDeath, self, self.DestructDeathHandler)
    EventCenter.Add(BattleUIEvtEnum.kBossReady, self, self.OnBossUIEvent)
    EventCenter.Add(BattleUIEvtEnum.kNewFloor, self, self.OnNewFloorUIEvent)
    EventCenter.Add(BattleEvtEnum.kDropGold, self, self.OnDropGold)
    EventCenter.Add(BattleEvtEnum.kDropExp, self, self.OnDropExp)
    EventCenter.Add(BattleEvtEnum.kSpawnBossMonster, self, self.OnSpawnBoss)
    EventCenter.Add(BattleEvtEnum.kDropEveryGold, self, self.OnDropEveryGold)
    EventCenter.Add(BattleEvtEnum.kDropEveryExp, self, self.OnDropEveryExp)

    EventCenter.Add(BattleUIEvtEnum.kEvilDeath, self, self.OnEvilDeathUIEvent)
    EventCenter.Add(BattleUIEvtEnum.kDestructDeath, self, self.OnEvilDeathUIEvent)

    EventCenter.Add(MysteriousnessEventEnum.kTargetConclude, self, self.TargetConclude)
    EventCenter.Add(MysteriousnessEventEnum.kTimeOut, self, handler(self,self.TimeOut))
    EventCenter.Add(MysteriousnessEventEnum.kTargetFailure, self, handler(self,self.TargetFailure))
    EventCenter.Add(BattleEvtEnum.kBossDeath, self, self.BossDeathHandler)
    EventCenter.Add(BattleEvtEnum.kFriendDeath, self, self.OnFriendDeathHandler)
    EventCenter.Add(SkillMsgEnum.kStartXp,self,self.OnXPStart)
    EventCenter.Add(TreasureMsgEnum.kGetTreasure,self,self.OnGetTreasure)
end

function BattleViewTopPanelBehaviour:OnGetTreasure(event)
    local mainId = event:GetParam("MainId")
    local subId = event:GetParam("SubId")
    logWarn("GetTreasure:"..mainId.." "..subId)
end

function BattleViewTopPanelBehaviour:AddExpAndGold(roleExp,petExp,gold)
    self.curExp = self.curExp + roleExp
    self.exp = self.exp + roleExp
    self.gold = self.gold + gold
    self.level,self.curExp = UpgradeModel.ComputerExp(self.level,self.curExp)
    DataCenter.Get(PetData):AddFightExp(petExp)
    self.heroData:SetLevel(self.level)
    self.heroData:SetExp(self.exp)
    self.heroData:SetGold(self.gold)
    self.heroData:SetCurExp(self.curExp)
    self.cointext.text = self:ChangeNumberToKBMT(self.gold)
    self:UpdateLevelUI()
end

function BattleViewTopPanelBehaviour:TargetConclude(event)
    local view = MysteriousnessResultViewBehaviour.new()
    local time = event:GetParam("Time")
    local success,finExp,finGold,finPetExp = view:SetDropReward(self.accGold,self.accExp,self.accRewardItem,time,true)
    self:AddExpAndGold(finExp,finPetExp,finGold)
    view:ShowToTop()
    EventCenter.Post(UpdateTaskEnum.kTaskCopyNumUpdate)
    if nil ~= self.mysteriousnessLogic then
        self.mysteriousnessLogic:Reset()
    end
end

function BattleViewTopPanelBehaviour:OnExitClick()
    local view = MysteriousnessResultViewBehaviour.new()
    local time = self.mysteriousnessLogic:GetRemainTime()
    local success,finExp,finGold,finPetExp = view:SetDropReward(self.accGold,self.accExp,self.accRewardItem,time,false)
    self:AddExpAndGold(finExp,finPetExp,finGold)
    view:ShowToTop()
    if nil ~= self.mysteriousnessLogic then
        self.mysteriousnessLogic:Reset()
    end
end

function BattleViewTopPanelBehaviour:TargetFailure()
    local view = MysteriousnessResultViewBehaviour.new()
    local currencyItem = self.currencyCheckPoint:GetByKey(self.mysteriousnessData:CurrGateId())
    local time = currencyItem:GetParameter(1)
    local success,finExp,finGold,finPetExp = view:SetDropReward(self.accGold,self.accExp,self.accRewardItem,time,false)
    self:AddExpAndGold(finExp,finPetExp,finGold)
    view:ShowToTop()
    if nil ~= self.mysteriousnessLogic then
        self.mysteriousnessLogic:Reset()
    end
end

function BattleViewTopPanelBehaviour:TimeOut()
    local view = MysteriousnessResultViewBehaviour.new()
    local currencyItem = self.currencyCheckPoint:GetByKey(self.mysteriousnessData:CurrGateId())
    local time = currencyItem:GetParameter(1)
    local success,finExp,finGold,finPetExp = view:SetDropReward(self.accGold,self.accExp,self.accRewardItem,time,false)
    self:AddExpAndGold(finExp,finPetExp,finGold)
    view:ShowToTop()
    if nil ~= self.mysteriousnessLogic then
        self.mysteriousnessLogic:Reset()
    end
end

function BattleViewTopPanelBehaviour:PlayExpImgAniamtion(loop)
    self.lvlImage.transform.localScale = Vector3.New(1.0,1.0,1.0)
    local tweeners = self.lvlImage.transform:GetComponents(typeof(DG.Tweening.DOTweenAnimation))
    local tbl = tweeners:ToTable()
    for i=1, table.maxn(tbl) do
        tbl[i].loops = loop
        tbl[i].loopType = DG.Tweening.LoopType.Restart
        tbl[i].hasOnComplete = true
        tbl[i]:CreateTween()
        local tween = tbl[i].tween
        tween:OnComplete(function()
            self.lvlImage.transform.localScale = Vector3.New(1.0,1.0,1.0)
        end)
        tbl[i]:DOPlay()
    end
end

function BattleViewTopPanelBehaviour:PlayExpImgMaskAnimation(loop)
    self.lvlImage2.transform.localScale = Vector3.New(1.0,1.0,1.0)
    self.lvlImage2.color = Color(1,1,1,1)
    local tweeners2 = self.lvlImage2.transform:GetComponents(typeof(DG.Tweening.DOTweenAnimation))
    local tbl2 = tweeners2:ToTable()
    for i=1, table.maxn(tbl2) do
        tbl2[i].loops = loop
        tbl2[i].loopType = DG.Tweening.LoopType.Restart
        tbl2[i].hasOnComplete = true
        tbl2[i]:CreateTween()
        local tween = tbl2[i].tween
        tween:OnComplete(function()
            self.lvlImage2.transform.localScale = Vector3.New(1.0,1.0,1.0)
            self.lvlImage2.color = Color(1,1,1,1)
        end)
        tbl2[i]:DOPlay()
    end
end

function BattleViewTopPanelBehaviour:OnDropEveryExp(event)
    
end

function BattleViewTopPanelBehaviour:PlayGoldImgAniamtion(loop)
    self.coinImg.transform.localScale = Vector3.New(1.0,1.0,1.0)
    local tweeners = self.coinImg.transform:GetComponents(typeof(DG.Tweening.DOTweenAnimation))
    local tbl = tweeners:ToTable()
    for i=1, table.maxn(tbl) do
        tbl[i].loops = loop
        tbl[i].loopType = DG.Tweening.LoopType.Restart
        tbl[i].hasOnComplete = true
        tbl[i]:CreateTween()
        local tween = tbl[i].tween
        tween:OnComplete(function()
            self.coinImg.transform.localScale = Vector3.New(1.0,1.0,1.0)
        end)
        tbl[i]:DOPlay()
    end

    self.cointext.transform.localScale = Vector3.New(1.0,1.0,1.0)
    local textTweeners = self.cointext.transform:GetComponents(typeof(DG.Tweening.DOTweenAnimation))
    local textTbl = textTweeners:ToTable()
    for i=1, table.maxn(textTbl) do
        textTbl[i].loops = loop
        textTbl[i].loopType = DG.Tweening.LoopType.Restart
        textTbl[i].hasOnComplete = true
        textTbl[i]:CreateTween()
        local tween = textTbl[i].tween
        tween:OnComplete(function()
            self.cointext.transform.localScale = Vector3.New(1.0,1.0,1.0)
        end)
        textTbl[i]:DOPlay()
    end
end

function BattleViewTopPanelBehaviour:PlayGoldImgMaskAnimation(loop)
    self.coinImg2.transform.localScale = Vector3.New(1.0,1.0,1.0)
    self.coinImg2.color = Color(1,1,1,1)
    local tweeners2 = self.coinImg2.transform:GetComponents(typeof(DG.Tweening.DOTweenAnimation))
    local tbl2 = tweeners2:ToTable()
    for i=1, table.maxn(tbl2) do
        tbl2[i].loops = loop
        tbl2[i].loopType = DG.Tweening.LoopType.Restart
        tbl2[i].hasOnComplete = true
        tbl2[i]:CreateTween()
        local tween = tbl2[i].tween
        tween:OnComplete(function()
            self.coinImg2.transform.localScale = Vector3.New(1.0,1.0,1.0)
            self.coinImg2.color = Color(1,1,1,1)
        end)
        tbl2[i]:DOPlay()
    end
end

function BattleViewTopPanelBehaviour:OnDropEveryGold(event)
    
end

function BattleViewTopPanelBehaviour:PlayGoldAnimation(time)
    local cnt = 1
    if self.goldCDtween ~= nil and self.goldCDtween:IsPlaying() then
        return
    else
        if self.rewardGoldEmitterCount <= 15 then
            cnt = 1
        elseif self.rewardGoldEmitterCount > 15 and self.rewardGoldEmitterCount <= 25 then
            cnt = 2
        else
            cnt = 3
        end
        self.rewardGoldEmitterCount = 0
        self.goldCDtween = DG.Tweening.DOVirtual.Float(1.0,0.0,time,function(x)
            end)
        self.goldCDtween:Play()
        self.goldCDtween:SetAutoKill(true)
    end
    self:PlayGoldImgAniamtion(cnt)
    self:PlayGoldImgMaskAnimation(cnt)
end

function BattleViewTopPanelBehaviour:PlayExpAnimation(time)
    local cnt = 1
    if self.expCDtween ~= nil and self.expCDtween:IsPlaying() then
        return
    else
        if self.rewardExpEmitterCount <= 15 then
            cnt = 1
        elseif self.rewardExpEmitterCount > 15 and self.rewardExpEmitterCount <= 25 then
            cnt = 2
        else
            cnt = 3
        end
        self.rewardExpEmitterCount = 0
        self.expCDtween = DG.Tweening.DOVirtual.Float(1.0,0.0,time,function(x)
            end)
        self.expCDtween:Play()
        self.expCDtween:SetAutoKill(true)
    end
    self:PlayExpImgAniamtion(cnt)
    self:PlayExpImgMaskAnimation(cnt)
end

function BattleViewTopPanelBehaviour:OnDropGold(event)
    self.tweenerCoinNum = self.tweenerCoinNum + 1
    self:PlayGoldAnimation(0.7)
end

function BattleViewTopPanelBehaviour:UpdateLevelUI()
    local nextlvItem = self.playLevelStatic:GetByKey(self.level)
    if nextlvItem then
        self.progressFront.fillAmount = self.curExp / nextlvItem:Exp()
    end 
    self.lvltext.text = string.format("%d",self.level)
end

function BattleViewTopPanelBehaviour:OnDropExp(event)
    self:UpdateLevelUI()
    self:PlayExpAnimation(0.7)
end

function BattleViewTopPanelBehaviour:Start()
    self.bagTf = self.transform.parent:FindChild("skillLoop/bagBtn")
end

function BattleViewTopPanelBehaviour:OnDestroy()
    EventCenter.Detach(self)
end

function BattleViewTopPanelBehaviour:DoFlyRewardsAni(pos)
    local goldenSprite = Util.LoadSprite ("UI/Common/icon_flygold")
    local expSprite = Util.LoadSprite ("UI/Common/icon_flyexp")

    RewardEmitter.Show(pos,self.coinImg.transform.position, goldenSprite,function (x)
        -- body
        local event = Event.new()
		event:AddParam("count",x)
        EventCenter.Post(BattleEvtEnum.kDropGold, event)
    end,function (x)
        if self.goldAudioCDtween == nil or self.goldAudioCDtween:IsPlaying() == false then
            self.goldAudioCDtween = DG.Tweening.DOVirtual.Float(1.0,0.0,0.8,function(x)end)
            self.goldAudioCDtween:Play()
            self.goldAudioCDtween:SetAutoKill(true)
            Singleton_MgrsContainer.Instance.soundMgr:PlayAudioPool("Audios/Battle/aud_gold",Vector3.zero,1,1,false)
        end
        local event = Event.new()
		event:AddParam("count",x)
        EventCenter.Post(BattleEvtEnum.kDropEveryGold, event)
    end,function(x)
        self.rewardGoldEmitterCount = self.rewardGoldEmitterCount + x
    end)
    RewardEmitter.Show(pos,self.lvlImage.transform.position, expSprite,function (x)
        -- body
        EventCenter.Post(BattleEvtEnum.kDropExp, nil)
    end,function (x)
        EventCenter.Post(BattleEvtEnum.kDropEveryExp, nil)
    end,function(x)
        self.rewardExpEmitterCount = self.rewardExpEmitterCount + x
    end)
end

function BattleViewTopPanelBehaviour:OnEvilDeathUIEvent()
    local battleData = DataCenter.Instance().BattleData
    local deathEvailRole = battleData.DeathEvailRole
    local pos = deathEvailRole.transform.position

    self:DoFlyRewardsAni(pos)

    local heroData = DataCenter.Get(HeroData)
    local mysteriousData = DataCenter.Get(MysteriousData)
    local currencyCheckPoint = StaticPool.Get(CurrencyCheckpointStatic)
    local childCheckPoint = StaticPool.Get(ChildCheckpointStatic)
    local battleData = DataCenter.Instance ().BattleData;
    local item = StaticPool.Get(CheckpointStatic):GetByKey (battleData.CheckPointId)
    if mysteriousData:IsMysteriousness() then
        --秘镜掉落
        local currencyItem = currencyCheckPoint:GetByKey(mysteriousData:CurrGateId())
        item = childCheckPoint:GetByKey(currencyItem:ChildId())
    end
    local curRewardItemList = RewardModel.RandomRewardItem(item,DropOwnterType.kMonster)
    for i=1,curRewardItemList:Size() do
        local curRewardItem = curRewardItemList:At(i)
        if nil == curRewardItem then
            return
        end 

        local findItem = self.accRewardItem:Find(curRewardItem:StaticId())
        if findItem ~= nil then
            local num = findItem:Num()
            findItem:SetNum(num + curRewardItem:Num())
        else
            self.accRewardItem:Insert(curRewardItem:StaticId(),curRewardItem)
        end

        local worldCamera = CameraGroup.Instance:GetFollowCamera ()
        local uiCamera = CameraGroup.Instance.uiCamera
        local uiCanvas = GameObject.Find ("2dUICanvas")
        local canvasTf = uiCanvas.transform

        local newPos = UIHelper.WorldToLocalPointInRect(pos,worldCamera,uiCamera,uiCanvas)
        
        local dropObj =  GameObject.New("DropObj")
        local img = dropObj:AddComponent(typeof(UnityEngine.UI.Image))
        img.sprite = Util.LoadSprite (curRewardItem:IconPath())
        img.rectTransform:SetParent(canvasTf, false)
        img.rectTransform.anchorMin = Vector2 (0.5, 0.5);
        img.rectTransform.anchorMax = Vector2 (0.5, 0.5);
        img.rectTransform.pivot = Vector2 (0.5, 0.5);
        img.rectTransform.localPosition = newPos
        img.rectTransform.localScale = Vector3.zero

        local sequence = DG.Tweening.DOTween.Sequence()
        local moveToScreenCenter = img.rectTransform:DOLocalMove(Vector2.New(0,250), 0.25, false)
        local scaleToOne = img.rectTransform:DOScale(1,0.25)
        local delay = DG.Tweening.DOVirtual.DelayedCall(1,handler(self,function()
            local delaySequence = DG.Tweening.DOTween.Sequence()
            local moveTo = img.rectTransform:DOMove(self.bagTf.position, 0.5, false)
            local scaleToZero = img.rectTransform:DOScale(0,0.5)
            delaySequence:Append(moveTo)
            delaySequence:Join(scaleToZero)
            delaySequence:AppendCallback(function()
                        GameObject.Destroy(dropObj)
                     end)
        end),false)


        sequence:Append(moveToScreenCenter)
        sequence:Join(scaleToOne)
        sequence:Append(delay)
    end
end

function BattleViewTopPanelBehaviour:OnChatClickEvent()
    local chatView = ChatViewBehaviour.new()
    chatView:ShowToTop()
end