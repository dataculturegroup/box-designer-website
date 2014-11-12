#!/usr/bin/env ruby 
require 'sinatra'

get '/' do
	"Worked on dreamhost"
end

get '/render' do
	result = `java -cp BOX-v.1.6.1.jar com.rahulbotics.boxmaker.CommandLine /Users/rahulb/Documents/workspace/boxmaker-all/boxmaker-web-app/tmp/boxes/box-20141112_142124_536961.pdf 101.6 152.4 127.0 4.7625 0.0 11.90625 false`
	"Result was #{result}"
end
