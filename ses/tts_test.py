import time, sys, torch, torchaudio
torch.set_num_threads(4)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
t=time.time()
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print("load", time.time()-t, flush=True)
text = "Yıl sekiz yüz kırk beş. Kuzeyin buz gibi sularında, yüz yirmi savaş gemisi yelken açıyor."
for ex,cfg in [(0.5,0.5)]:
    t=time.time()
    wav = m.generate(text, language_id="tr", audio_prompt_path="/home/user/Viking/.models/tr_m.flac", exaggeration=ex, cfg_weight=cfg)
    dur = wav.shape[-1]/m.sr
    print(f"ex={ex} cfg={cfg} gen {time.time()-t:.1f}s for {dur:.1f}s audio", flush=True)
    torchaudio.save(f"/home/user/Viking/build/test/chatter_{ex}_{cfg}.wav", wav, m.sr)
