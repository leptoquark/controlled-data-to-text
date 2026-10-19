import argparse
import json
from pathlib import Path
from .synthetic import make_dataset, save, load
from .engine import generate
def main():
    parser=argparse.ArgumentParser(description="Laboratorio data-to-text controllato")
    sub=parser.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('synth'); s.add_argument('--n',type=int,default=1200); s.add_argument('--seed',type=int,default=42); s.add_argument('--output',default='data/synthetic.jsonl')
    e=sub.add_parser('experiment'); e.add_argument('--data',default='data/synthetic.jsonl'); e.add_argument('--output',default='results/latest'); e.add_argument('--seed',type=int,default=42); e.add_argument('--bootstrap',type=int,default=200)
    g=sub.add_parser('generate'); g.add_argument('input'); g.add_argument('--output',default='results/generated.json')
    a=parser.parse_args()
    if a.cmd=='synth':
        if a.n<100: parser.error('Usare almeno 100 profili per il laboratorio')
        docs=make_dataset(a.n,a.seed); save(docs,a.output)
        Path(a.output).with_suffix('.example.json').write_text(json.dumps(docs[0],ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{len(docs)} profili sintetici salvati in {a.output}')
    elif a.cmd=='experiment':
        from .experiment import run
        print(json.dumps(run(load(a.data),a.output,a.seed,a.bootstrap),ensure_ascii=False,indent=2))
    else:
        result=generate(json.loads(Path(a.input).read_text(encoding='utf-8')))
        p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(result['status'])
        if result['status']=='blocked': raise SystemExit(2)
if __name__=='__main__': main()
