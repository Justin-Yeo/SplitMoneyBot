from enum import Enum

class ConvState(str, Enum):
    SELECT_USERS = "SelectUsers"  
    SELECT_PAYER = "SelectPayer" 
    ENTER_AMOUNT = "EnterAmount"  
    ENTER_REASON = "EnterReason"  
    CANCEL = "Cancel"
    SELECT_EXPENSE = "SelectExpense"
    EDIT_OPTION = "EditOption"
    SELECT_PAYER_NEW = "SelectPayerNew"
    SELECT_USERS_NEW = "SelectUsersNew"
    EDIT_AMOUNT = "EditAmount"  
    EDIT_REASON = "EditReason" 