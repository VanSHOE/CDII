import subprocess
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts Quora or ShareChat data to a graph')
    
    parser.add_argument('-i','--input', dest='input', type=str, help='Input folder path for Quora or Input .json file path for ShareChat')
    parser.add_argument('-o','--output', dest='output', type=str, help='Output folder path')
    parser.add_argument('-t','--type', dest='type', type=str, help='quora posts[QP], quora users[QU] or sharechat[S]')
    parser.add_argument('-n','--name', dest='name', type=str, help='Output file name')
    parser.add_argument('-u', '--user_input_paths', dest='user_input_paths', type=str)
    
    args = parser.parse_args()
    if args.type == 'QP':
        cmd = ['python', './src/graph_quora.py', '-i', args.input, '-o', args.output, '-n', args.name]
        if args.user_input_paths:
            cmd.append('-u')
            cmd.append(args.user_input_paths)
        subprocess.call(cmd)
    elif args.type == 'QU':
        subprocess.call(['python', './src/graph_user_quora.py', '-i', args.input, '-o', args.output, '-n', args.name])
    elif args.type == 'S':
        subprocess.call(['python', './src/graph_sc.py', '-i', args.input, '-o', args.output, '-n', args.name])
    else:
        print('Invalid type')
        exit(1)