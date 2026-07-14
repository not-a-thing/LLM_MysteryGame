import time

class GameState:
    def __init__(self):
        self.current_screen='name_entry'
        self.player_name=""
        self.name_input_active=False
        self.active_chat=None
        
        self.chapter=1
        self.chapter_data=None
        
        self.suspicion_points=0
        self.investigation_progress=0
        self.martha_pressure=0
        
        
        self.chapter_checkpoint_reached=False
        self.chapter_transition_active=False
        self.chapter_transition_alpha=0
        self.chapter_transition_target=None
        self.pending_chapter_fade=False
        
        self.intro_scene_index=0
        self.intro_phase="background_fade_in"
        self.intro_alpha=0
        self.intro_last_update=0
        
        self.unknown_unlocked=False
        self.unknown_intro_done=False
        self.unknown_is_active=False
        
        self.pending_choices=[]
        
        self.typing_contact=None
        self.typing_started_at=0
        self.typing_duration=0
        self.queued_messages=[]
        
        self.martha_waiting=False
        self.martha_result=None
        self.martha_thread=None

        self.evaluator_waiting=False
        self.evaluator_result=None
        self.evaluator_thread=None

        self.last_evaluation=None
        
        self.messages={
            "Martha":[],
            "Unknown":[],
        }
        
        self.unread_counts={
            "Martha":0,
            "Unknown":0,
        }
        
        self.contact_status={
            "Martha":{
                "is_active": True,
                "is_typing": False,
                "last_seen": None,
            },
            "Unknown":{
                "is_active": False,
                "is_typing": False,
                "last_seen": None,
            }
        }
        
        self.notification={
            "visible":False,
            "sender":"",
            "message":"",
            "shown_at":0,
            "duration":3500,
        }
        
        self.revealed_facts={
            "martha_admitted_argument": False,
            "martha_admitted_saw_sarah": False,
            "martha_admitted_push":False,
            "sarah_is_alive": False,
            "player_research_secret":False,
        }
        
        self.evaluator_memory={
            "chapter_1_summary":"",
            "repeated_topics":[],
        }
    def set_contact_active(self,contact_name,is_active):
        status=self.contact_status[contact_name]
        status["is_active"]=is_active
        status["is_typing"]=False
        if not is_active:
            status["last_seen"]=time.time()
    
    def set_contact_typing(self, contact_name, is_typing):
        status=self.contact_status[contact_name]
        status["is_typing"]=is_typing
        if is_typing:
            status["is_active"]=True