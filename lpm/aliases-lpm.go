package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"os"
	"sync"
	"time"

	flags "github.com/jessevdk/go-flags"
	"github.com/yl2chen/cidranger"
)

var opts struct {
	AliasedFile    string `short:"a" long:"aliased-file" required:"true" description:"File containing aliased prefixes"`
	NonAliasedFile string `short:"n" long:"non-aliased-file" required:"true" description:"File containing non-aliased prefixes"`
	IPAddressFile  string `short:"i" long:"ip-address-file" required:"true" description:"File containing IP addresses to be matched against (non-)aliased prefixes"`
}

type apdRangerEntry struct {
	ipNet   net.IPNet
	aliased bool
}

func (a *apdRangerEntry) Network() net.IPNet {
	return a.ipNet
}

func readAliased(ranger cidranger.Ranger, filename string) {
	fillTree(ranger, filename, true)
}

func readNonAliased(ranger cidranger.Ranger, filename string) {
	fillTree(ranger, filename, false)
}

func fillTree(ranger cidranger.Ranger, filename string, aliased bool) {

	fh, err := os.Open(filename)
	if err != nil {
		log.Println("opening file:", err)
		return
	}
	defer fh.Close()
	scanner := bufio.NewScanner(fh)

	for scanner.Scan() {
		line := scanner.Text()
		if err := scanner.Err(); err != nil {
			log.Println("reading input:", err)
		}
		_, network, err := net.ParseCIDR(line)
		if err != nil {
			log.Println("parsing CIDR ", line, ": ", err)
		} else {
			ranger.Insert(&apdRangerEntry{*network, aliased})
		}
	}
}

func findLongestPrefix(ranger cidranger.Ranger, inputChan <-chan string, outputChan chan<- []byte) {

	for line, ok := <-inputChan; ok; line, ok = <-inputChan {

		ip := net.ParseIP(line)
		if ip == nil {
			log.Println("Could not parse IP ", line)
			continue
		}

		networks, err := ranger.ContainingNetworks(ip)
		if err != nil {
			log.Println("containing networks: ", err)
		}

		mostSpecific := (networks[len(networks)-1]).(*apdRangerEntry)
		var aliasedStr string
		if mostSpecific.aliased {
			aliasedStr = "1"
		} else {
			aliasedStr = "0"
		}

		outputChan <- []byte(fmt.Sprintf("%s,%s,%s", line, mostSpecific.ipNet.String(), aliasedStr))
	}
}

func readInput(inputChan chan<- string, filename string) {

	defer close(inputChan)

	fh, err := os.Open(filename)
	if err != nil {
		log.Println("opening file:", err)
		return
	}
	defer fh.Close()
	scanner := bufio.NewScanner(fh)

	for scanner.Scan() {
		line := scanner.Text()
		if err := scanner.Err(); err != nil {
			log.Println("reading input:", err)
		}
		inputChan <- line
	}
}

func outputResult(outputChan <-chan []byte) {

	fh := bufio.NewWriter(os.Stdout)
	defer fh.Flush()

	newline := []byte("\n")

	for resBytes := range outputChan {
		fh.Write(resBytes)
		fh.Write(newline)
	}
}

func main() {

	// Parse command line arguments
	parser := flags.NewParser(&opts, flags.Default)
	if _, err := parser.Parse(); err != nil {
		if err.(*flags.Error).Type == flags.ErrHelp {
			return
		} else if err.(*flags.Error).Type != flags.ErrRequired {
			log.Fatal(err)
		} else {
			os.Exit(1)
		}
	}

	// Store aliased and non-aliased prefixes in a single trie
	ranger := cidranger.NewPCTrieRanger()

	// Read aliased and non-aliased prefixes
	readAliased(ranger, opts.AliasedFile)
	readNonAliased(ranger, opts.NonAliasedFile)

	// Multiprocessing using goroutines
	numRoutines := 1000
	inputChan := make(chan string)
	outputChan := make(chan []byte)

	// Read targets, find longest prefix and print output
	// wg makes sure that all processing goroutines have terminated before exiting
	var wg sync.WaitGroup
	// This 1 is for the main goroutine and makes sure that the output is not immediately closed
	wg.Add(1)

	go func() {
		// Close output channel when all processing goroutines finish
		defer close(outputChan)
		wg.Wait()
	}()

	// Start goroutines for longest prefix matching
	for i := 0; i < numRoutines; i++ {
		go func() {
			wg.Add(1)
			findLongestPrefix(ranger, inputChan, outputChan)
			wg.Done()
		}()
	}

	// Start goroutine for input reading
	go readInput(inputChan, string(opts.IPAddressFile))

	time.Sleep(1000 * time.Millisecond)
	wg.Done()

	// Start output writing
	outputResult(outputChan)
}
