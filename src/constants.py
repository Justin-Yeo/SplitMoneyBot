from enum import Enum

class ConvState(str, Enum):
    SELECT_USERS = "SelectUsers"  
    SELECT_PAYER = "SelectPayer" 
    ENTER_AMOUNT = "EnterAmount"  
    ENTER_REASON = "EnterReason"  
    CANCEL = "Cancel"
    CONFIRM_SELECTION = "CONFIRM_SELECTION"