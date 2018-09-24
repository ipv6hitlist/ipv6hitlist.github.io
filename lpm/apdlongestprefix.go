package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"os"
	"strconv"
	"sync"
	"time"

	flags "github.com/jessevdk/go-flags"
	"github.com/yl2chen/cidranger"
)

var opts struct {
	// input-dpd-dir (instead of input-apd-dir) for backwards compatibility
	InputAPDDir string `short:"i" long:"input-dpd-dir" required:"true" description:"Directory with APD output files"`
	Date        string `short:"d" long:"date" required:"true" description:"Date and time in YYYY-MM-DD-HHMM of input files"`
	TargetFile  string `short:"f" long:"target-file" required:"true" description:"Target file for which lookup should be performed"`
}

type apdRangerEntry struct {
	//	cidranger.RangerEntry
	ipNet   net.IPNet
	aliased bool
}

func (a *apdRangerEntry) Network() net.IPNet {
	return a.ipNet
}

func readAliased(ranger cidranger.Ranger, filename string) {
	fillTree(ranger, filename, true)
}

func readNonaliased(ranger cidranger.Ranger, filename string) {
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
		//outputChan <- []byte(fmt.Sprintf(    line + "," + mostSpecific.ipNet.String() + "," + aliasedStr)
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

	ranger := cidranger.NewPCTrieRanger()

	// Read prefix-based APD results
	// 2018-04-25-2300.csv.dpdprefix.pfxonly.sortu.dense
	// 2018-04-25-2300.csv.dpdprefix.pfxonly.sortu.nondense
	readAliased(ranger, opts.InputAPDDir+"/"+opts.Date+".csv.dpdprefix.pfxonly.sortu.sw3.dense")
	readNonaliased(ranger, opts.InputAPDDir+"/"+opts.Date+".csv.dpdprefix.pfxonly.sortu.sw3.nondense")

	// Read target-based DPD results
	// 2018-04-25-2300.csv.dpdtarget.slash100.threshold.pfxonly.randomips.pfxonly.sortu.dense
	// 2018-04-25-2300.csv.dpdtarget.slash100.threshold.pfxonly.randomips.pfxonly.sortu.nondense
	for i := 64; i <= 124; i += 4 {
		readAliased(ranger, opts.InputAPDDir+"/"+opts.Date+".csv.dpdtarget.slash"+strconv.Itoa(i)+".threshold.pfxonly.randomips.pfxonly.sortu.sw3.dense")
		readNonaliased(ranger, opts.InputAPDDir+"/"+opts.Date+".csv.dpdtarget.slash"+strconv.Itoa(i)+".threshold.pfxonly.randomips.pfxonly.sortu.sw3.nondense")
	}

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
	go readInput(inputChan, string(opts.TargetFile))

	time.Sleep(1000 * time.Millisecond)
	wg.Done()

	// Start output writing
	outputResult(outputChan)
}
